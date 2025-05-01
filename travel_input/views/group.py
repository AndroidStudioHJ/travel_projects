from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib.auth.mixins import LoginRequiredMixin
from django.views.generic import ListView, DetailView, CreateView, UpdateView, DeleteView
from django.urls import reverse_lazy
from django.http import JsonResponse
from ..models import GroupTravel, GroupMember, GroupMessage

def group_travel(request):
    return render(request, 'travel_input/group_travel.html')

class GroupTravelListView(LoginRequiredMixin, ListView):
    model = GroupTravel
    template_name = 'travel_input/group_travel_list.html'
    context_object_name = 'groups'

    def get_queryset(self):
        return GroupTravel.objects.filter(members=self.request.user)

class GroupTravelDetailView(LoginRequiredMixin, DetailView):
    model = GroupTravel
    template_name = 'travel_input/group_travel_detail.html'
    context_object_name = 'group'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['messages'] = GroupMessage.objects.filter(group=self.object).order_by('created_at')
        context['is_admin'] = self.object.created_by == self.request.user
        return context

class GroupTravelCreateView(LoginRequiredMixin, CreateView):
    model = GroupTravel
    template_name = 'travel_input/group_travel_form.html'
    fields = ['name', 'description', 'schedule']
    success_url = reverse_lazy('travel_input:group_travel_list')

    def form_valid(self, form):
        form.instance.created_by = self.request.user
        response = super().form_valid(form)
        GroupMember.objects.create(group=form.instance, user=self.request.user, is_admin=True)
        return response

class GroupTravelUpdateView(LoginRequiredMixin, UpdateView):
    model = GroupTravel
    template_name = 'travel_input/group_travel_form.html'
    fields = ['name', 'description']
    success_url = reverse_lazy('travel_input:group_travel_list')

    def get_queryset(self):
        return GroupTravel.objects.filter(created_by=self.request.user)

class GroupTravelDeleteView(LoginRequiredMixin, DeleteView):
    model = GroupTravel
    success_url = reverse_lazy('travel_input:group_travel_list')

    def get_queryset(self):
        return GroupTravel.objects.filter(created_by=self.request.user)

@login_required
def join_group(request, pk):
    group = get_object_or_404(GroupTravel, pk=pk)
    if not GroupMember.objects.filter(group=group, user=request.user).exists():
        GroupMember.objects.create(group=group, user=request.user)
    return redirect('travel_input:group_travel_detail', pk=pk)

@login_required
def leave_group(request, pk):
    group = get_object_or_404(GroupTravel, pk=pk)
    GroupMember.objects.filter(group=group, user=request.user).delete()
    return redirect('travel_input:group_travel_list')

@login_required
def send_message(request, pk):
    if request.method == 'POST':
        group = get_object_or_404(GroupTravel, pk=pk)
        content = request.POST.get('content')
        if content:
            GroupMessage.objects.create(
                group=group,
                user=request.user,
                content=content
            )
        return JsonResponse({'status': 'success'})
    return JsonResponse({'status': 'error'}, status=400) 