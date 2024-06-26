"""
ビュー定義です。
"""
import datetime
from functools import wraps

from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.contrib.auth.mixins import AccessMixin, LoginRequiredMixin
from django.contrib.auth.views import LoginView, LogoutView, PasswordChangeView
from django.db.models import Q
from django.http import HttpResponseForbidden
from django.http.response import JsonResponse
from django.shortcuts import redirect
from django.urls import reverse, reverse_lazy
from django.utils import dateformat
from django.views.generic import FormView, TemplateView

import timecard.settings
from worktime.forms import (CustomAuthenticationForm, CustomPasswordChangeForm,
                            TimeOffListForm, TimeOffRequestForm,
                            TimeOffStatusForm, TimeRecordCalendarForm,
                            TimeRecordForm, TimeRecordSummaryForm)
from worktime.models import TimeOffPattern, TimeOffRequest, TimeRecord
from worktime.queries import count_time_off_requests, get_monthly_records
from worktime.rules import summarize
from worktime.utils import (display_name, get_first_day_of_year, get_users,
                            get_year_range)


class StaffRequiredMixin(AccessMixin):
    """スタッフ権限を要求するミックスイン
    """

    def dispatch(self, request, *args, **kwargs):
        if not request.user.is_staff:
            return self.handle_no_permission()
        return super().dispatch(request, *args, **kwargs)


class UserLogin(LoginView):
    """ログイン画面のビュー
    """
    form_class = CustomAuthenticationForm
    template_name = 'worktime/auth_login.html'
    redirect_authenticated_user = True


class UserLogout(LogoutView):
    """ログアウト画面のビュー
    """
    pass


class PasswordChange(LoginRequiredMixin, PasswordChangeView):
    """パスワード変更画面のビュー
    """
    form_class = CustomPasswordChangeForm
    template_name = 'worktime/password_change.html'
    success_url = reverse_lazy('worktime:record')

    def form_valid(self, form):
        """バリデーション成功
        """
        messages.success(self.request, 'パスワードが更新されました')
        return super().form_valid(form)


class TimeRecordView(LoginRequiredMixin, FormView):
    """打刻画面のビュー
    """
    form_class = TimeRecordForm
    template_name = 'worktime/record.html'
    success_url = reverse_lazy('worktime:record')

    def get_context_data(self, *args, **kwargs):
        """コンテキストの返却
        """
        context = super().get_context_data(*args, **kwargs)
        context["is_enable_check_location"] = timecard.settings.ENABLE_CHECK_LOCATION
        context["is_enable_record_sound"] = timecard.settings.ENABLE_RECORD_SOUND
        context["is_enable_record_vibrate"] = timecard.settings.ENABLE_RECORD_VIBRATE
        context["display_name"] = display_name(self.request.user)
        context["recent"] = TimeRecord.objects.filter(
            username=self.request.user.username
        ).order_by("-date", "-time")[:10]
        context["actions"] = timecard.settings.RECORD_ACTIONS
        return context

    def string_to_float(self, string: str) -> float:
        """文字列を数値で取得します。

        Args:
            string (str): 文字列

        Returns:
            float: 数値
        """
        return float(string) if string else None

    def form_valid(self, form):
        """バリデーション成功
        """
        now = datetime.datetime.now()
        action = form.cleaned_data['action']
        TimeRecord.objects.create(
            date=now.date(),
            time=now.time(),
            username=self.request.user.username,
            action=action,
            latitude=self.string_to_float(form.cleaned_data['latitude']),
            longitude=self.string_to_float(form.cleaned_data['longitude']),
            accuracy=self.string_to_float(form.cleaned_data['accuracy']),
            ua=form.cleaned_data['ua'],
        )
        messages.success(
            self.request,
            timecard.settings.RECORD_ACTIONS.get(action) + 'の打刻が完了しました'
        )
        return super().form_valid(form)


class TimeOffListView(StaffRequiredMixin, FormView):
    """休暇承認画面のビュー
    """
    form_class = TimeOffListForm
    template_name = 'worktime/time_off_list.html'
    success_url = reverse_lazy('worktime:time_off_list')

    def get_context_data(self, *args, **kwargs):
        """コンテキストの返却
        """
        context = super().get_context_data(*args, **kwargs)
        records = TimeOffRequest.objects.filter(accepted=False).values(
            'id',
            'date',
            'username',
            'display_name',
            'created_at',
            'contact'
        ).order_by('date')
        entries = []
        for record in records:
            year = get_first_day_of_year(record['date']).year
            year_range = get_year_range(year)
            counts = count_time_off_requests(record['username'], year_range)
            entries.append({
                'id': record['id'],
                'year': year,
                'date': record['date'],
                'username': record['username'],
                'display_name': record['display_name'],
                'created_at': record['created_at'],
                'count': counts.get(record['display_name'], 0),
                'contact': record['contact']
            })
        context['entries'] = entries
        context['users'] = get_users(False)
        return context


class TimeOffStatusView(StaffRequiredMixin, FormView):
    """休暇集計画面のビュー
    """
    form_class = TimeOffStatusForm
    template_name = 'worktime/time_off_status.html'
    success_url = reverse_lazy('worktime:time_off_status')

    def get_context_data(self, *args, **kwargs):
        """コンテキストの返却
        """
        context = super().get_context_data(*args, **kwargs)
        today = datetime.datetime.today()
        first_day_of_year = get_first_day_of_year(today)
        context['year'] = int(self.request.GET.get(
            'year', first_day_of_year.year
        ))
        context['years'] = range(
            first_day_of_year.year - 9,
            first_day_of_year.year + 1
        )
        context['current_year'] = first_day_of_year.year
        context['entries'] = []
        display_names = []
        for id, name in get_users(True).items():
            counts = count_time_off_requests(
                id, get_year_range(context['year'])
            )
            for display_name in counts.keys():
                if not display_name in display_names:
                    display_names.append(display_name)
            if 0 < len(counts):
                context['entries'].append({
                    'id': id,
                    'name': name,
                    'counts': counts
                })
        context['display_names'] = sorted(display_names)
        return context


class TimeOffRequestView(LoginRequiredMixin, FormView):
    """休暇申請画面のビュー
    """
    form_class = TimeOffRequestForm
    template_name = 'worktime/time_off_request.html'
    success_url = reverse_lazy('worktime:time_off_request')

    def get_context_data(self, *args, **kwargs):
        """コンテキストの返却
        """
        context = super().get_context_data(*args, **kwargs)
        today = datetime.datetime.today()
        first_day_of_year = get_first_day_of_year(today)
        context["entries"] = TimeOffRequest.objects.filter(username=self.request.user.username).filter(
            Q(date__gte=first_day_of_year) | Q(accepted=False)
        ).distinct().order_by("date")
        context["counts"] = count_time_off_requests(
            self.request.user.username, get_year_range(first_day_of_year.year)
        )
        return context

    def form_valid(self, form):
        """バリデーション成功
        """
        request_date = form.cleaned_data['request_date']
        records = TimeOffRequest.objects.filter(
            date=request_date, username=self.request.user.username)
        if records.exists():
            form.add_error('request_date', '指定した日には既に申請が存在します')
            return self.form_invalid(form)
        pattern = TimeOffPattern.objects.get(
            id=form.cleaned_data['pattern_id']
        )
        TimeOffRequest.objects.create(
            date=request_date,
            username=self.request.user.username,
            display_name=pattern.display_name,
            contact=form.cleaned_data['contact'],
            attendance=pattern.attendance,
            begin=pattern.begin,
            end=pattern.end,
            leave=pattern.leave,
            back=pattern.back,
            accepted=False
        )
        messages.success(
            self.request,
            dateformat.format(request_date, 'Y/m/d (D)') +
            ' の ' + pattern.display_name + ' を申請しました'
        )
        return super().form_valid(form)


class TimeRecordCalendarView(LoginRequiredMixin, FormView):
    """勤務表画面のビュー
    """
    form_class = TimeRecordCalendarForm
    template_name = 'worktime/record_calendar.html'

    def get_context_data(self, **kwargs):
        """コンテキストの返却
        """
        context = super().get_context_data(**kwargs)
        if self.request.user.is_staff:
            context['username'] = self.request.GET.get(
                'username', self.request.user.username)
        else:
            context['username'] = self.request.user.username
        today = datetime.datetime.today()
        context['year'] = int(self.request.GET.get('year', today.year))
        context['month'] = int(self.request.GET.get('month', today.month))
        context['entries'] = get_monthly_records(
            context['username'], context['year'], context['month']
        )
        context['summary'] = summarize(context['entries'])
        context['users'] = get_users(False)
        return context

    def get_initial(self):
        """初期値の取得
        """
        initial = super().get_initial()
        initial['username'] = self.request.GET.get(
            'username', self.request.user.username
        )
        return initial

    def form_valid(self, form):
        """バリデーション成功
        """
        username = form.cleaned_data['username']
        year = form.cleaned_data['year']
        month = form.cleaned_data['month']
        return redirect(reverse('worktime:record_calendar') + f'?username={username}&year={year}&month={month}')


class TimeRecordSummaryView(StaffRequiredMixin, FormView):
    """勤務集計画面のビュー
    """
    form_class = TimeRecordSummaryForm
    template_name = 'worktime/record_summary.html'

    def get_context_data(self, **kwargs):
        """コンテキストの返却
        """
        context = super().get_context_data(**kwargs)
        today = datetime.datetime.today()
        context['year'] = int(self.request.GET.get('year', today.year))
        context['month'] = int(self.request.GET.get('month', today.month))
        return context

    def form_valid(self, form):
        """バリデーション成功
        """
        year = form.cleaned_data['year']
        month = form.cleaned_data['month']
        return redirect(reverse('worktime:record_summary') + f'?year={year}&month={month}')


def staff_required(func):
    """スタッフ権限を要求するデコレータ
    """
    @wraps(func)
    def wrapped_func(request, *args, **kwargs):
        if not request.user.is_staff:
            return HttpResponseForbidden('Forbidden')
        return func(request, *args, **kwargs)
    return wrapped_func


@staff_required
def time_off_accept(request):
    """休暇申請の承認処理 (画面なし)

    Args:
        request: リクエスト情報
        id: 承認するデータのID

    Returns:
        レスポンス情報
    """
    id = request.POST.get('id', None)
    record = TimeOffRequest.objects.filter(id=id).first()
    if record:
        if record.accepted:
            messages.warning(request, '指定された申請は既に承認済です')
        else:
            record.accepted = True
            record.save()
            users = get_users(False)
            messages.success(
                request,
                users.get(record.username, record.username) + ' の ' +
                dateformat.format(
                    record.date, 'Y/m/d (D)'
                ) + ' の ' + record.display_name + ' を承認しました'
            )
    else:
        messages.error(request, '指定された申請は存在しないか既に取り消されています')
    return redirect('worktime:time_off_list')


@staff_required
def time_off_cancel(request):
    """休暇申請の取り消し処理 (画面なし)

    Args:
        request: リクエスト情報
        id: 取り消すデータのID

    Returns:
        レスポンス情報
    """
    id = request.POST.get('id', None)
    record = TimeOffRequest.objects.filter(
        id=id, username=request.user.username
    ).first()
    if record:
        if record.accepted:
            messages.warning(request, '承認済の申請は取り消しできません')
        else:
            record.delete()
            messages.success(
                request,
                dateformat.format(
                    record.date, 'Y/m/d (D)'
                ) + ' の ' + record.display_name + ' を取り消しました')
    else:
        messages.error(request, '指定された申請は存在しないか既に取り消されています')
    return redirect('worktime:time_off_request')


class ReadmeView(TemplateView):
    """説明画面のビュー
    """
    template_name = 'worktime/readme.html'

    def get_context_data(self, *args, **kwargs):
        """コンテキストの返却
        """
        context = super().get_context_data(*args, **kwargs)
        context['IS_STAFF'] = self.request.user.is_staff
        context["MAX_DISTANCE"] = timecard.settings.MAX_DISTANCE
        context["YEAR_FIRST_MONTH"] = timecard.settings.YEAR_FIRST_MONTH
        context["ENABLE_CHECK_LOCATION"] = timecard.settings.ENABLE_CHECK_LOCATION
        return context


@staff_required
def api_users_list(request):
    """登録ユーザの一覧を取得

    Args:
        request: リクエスト情報

    Returns:
        json レスポンス
    """
    return JsonResponse(get_users(True))


@staff_required
def api_record_summary(request):
    """指定したユーザと年月の打刻記録のサマリを取得

    Args:
        request: リクエスト情報

    Returns:
        json レスポンス
    """
    id = request.GET.get('id', None)
    today = datetime.datetime.today()
    year = int(request.GET.get('year', today.year))
    month = int(request.GET.get('month', today.month))
    records = get_monthly_records(id, year, month)
    summary = summarize(records)
    return JsonResponse(summary)
