from django.urls import path
from core.views import views
from django.conf import settings
from django.conf.urls.static import static
from core.views import Child, Professor, User, Parent, Family, Event, ReportChild, Bill, ClassGroup, Alert, Activity, Gallery, AssistanceDaily

app_name = 'core'

urlpatterns = [
    path('', views.index, name='index'),
    path('notify_list/', views.notify_list, name='notify_list'),
    path('terms/', views.terms, name='terms'),
    path('createuparents/', views.create_user_parents, name='create_user_parents'),
    path('terms/set_status_terms', views.set_status_terms, name='set_status_terms'),
    

    # Child
    path('child/', Child.ChildListView.as_view(), name='child-list'),
    path('child/new/', Child.ChildStepOneCreateView.as_view(), name="child-add-one"),   
    path('child/new_two/<pk>', Child.ChildStepTwoCreateView.as_view(), name="child-add-two"),
    path('child/new_three/<int:pk>/', Child.ChildStepThreeCreateView.as_view(), name='child-add-three'),
    path('child/new_four/<int:pk>/', Child.ChildStepFourCreateView.as_view(), name="child-add-four"),
    path('child/new_five/<int:pk>/', Child.ChildStepFiveCreateView.as_view(), name="child-add-five"),
    path('save_relationship', Child.save_relationship, name="save-relationship"),
    path('save_approved', Child.save_approved, name="save-approved"),
    path('child/<pk>/', Child.ChildDetailView.as_view(), name="child-details"),
    path('child/<pk>/edit/', Child.ChildEditView.as_view(), name='child-edit'),
    path('child/<int:pk>/delete/', Child.ChildDeleteView.as_view(), name="child-delete"), 
    path('child_history/', Child.ChildListHistoryView.as_view(), name='child-history'),
    

    # Professor
    path('professor/', Professor.ProfessorListView.as_view(), name='professor-list'),
    path('professor/new/', Professor.ProfessorCreateView.as_view(), name="professor-add"),  
    path('professor/<int:pk>/delete/', Professor.ProfessorDeleteView.as_view(), name="professor-delete"), 
    path('professor/<pk>/edit/', Professor.ProfessorEditView.as_view(), name='professor-edit'),
    path('professor/<pk>/', Professor.ProfessorDetailView.as_view(), name="professor-details"),
    path('professor/profile/<str:pk>/', Professor.profile_professor, name="professor-details-user"),
    path('professor_history/', Professor.ProfessorListHistoryView.as_view(), name='professor-history'),   
    path('dailyProf/', AssistanceDaily.save_daily_professor, name='save_daily_professor'),    
    
    # User
    path('user/new/', User.UserCreateView.as_view(), name="user-add"),
    path('user/', User.UserListView.as_view(), name='user-list'),
    path('user/<int:pk>/delete/', User.UserDeleteView.as_view(), name="user-delete"), 
    path('user/<pk>/edit/', User.UserEditView.as_view(), name='user-edit'),
    path('user_history/', User.UserListHistoryView.as_view(), name='user-history'),

    # Parent
    path('parent/', Parent.ParentListView.as_view(), name='parent-list'),
    path('parent/new/', Parent.ParentCreateView.as_view(), name="parent-add"),  
    path('parent/<int:pk>/delete/', Parent.ParentDeleteView.as_view(), name="parent-delete"), 
    path('parent/<pk>/edit/', Parent.ParentEditView.as_view(), name='parent-edit'),
    path('parent/profile/<str:pk>/', Parent.profile_parent, name="parent-profile"),
    path('parent/<pk>/', Parent.ParentDetailView.as_view(), name="parent-details"),
    path('parent_history/', Parent.ParentListHistoryView.as_view(), name='parent-history'),

    # Family
    path('family/', Family.FamilyListView.as_view(), name='family-list'),
    path('family/new/', Family.FamilyCreateView.as_view(), name="family-add"),    
    path('family/<int:pk>/delete/', Family.FamilyDeleteView.as_view(), name="family-delete"), 
    path('family/<pk>/edit/', Family.FamilyEditView.as_view(), name='family-edit'),
    path('status_approved/<pk>/', Family.status_approved, name="status_approved"),
    path('status_reject/<pk>/', Family.status_reject, name="status_reject"),

    # Event
    path('event/', Event.EventListView.as_view(), name='event-list'),
    path('event/new/', Event.EventCreateView.as_view(), name='event-add'),
    path('event/<pk>/edit/', Event.EventEditView.as_view(), name='event-edit'),
    path('event/<pk>/delete/', Event.EventDeleteView.as_view(), name='event-delete'),
    path('event/calendar', Event.CalendarListView.as_view(), name='event-calendar'),
    path('get_events', Event.get_events, name='get_events'),

    # ReportChild
    path('report/', ReportChild.ReportChildListView.as_view(), name='report-list'),
    path('report/<pk>', ReportChild.ReportChildListAllView.as_view(), name='report-all'),
    path('report/new/<pk>/', ReportChild.ReportChildCreateView.as_view(), name='report-add'),
    path('report/<pk>/edit/', ReportChild.ReportChildEditView.as_view(), name='report-edit'),
    path('report/<pk>/delete/', ReportChild.ReportChildDeleteView.as_view(), name='report-delete'),
    path('report_history/', ReportChild.ReportChildListHistoryView.as_view(), name='report-history'),

    # Bill
    path('bill/', Bill.BillListView.as_view(), name='bill-list'),
    path('bill/new/', Bill.BillCreateView.as_view(), name='bill-add'),
    path('bill/<pk>/edit/', Bill.BillEditView.as_view(), name='bill-edit'),
    path('bill/<pk>/delete/', Bill.BillDeleteView.as_view(), name='bill-delete'),
    path('get_data', Bill.get_data, name="get_data"),
    path('bill_history/', Bill.BillListHistoryView.as_view(), name='bill-history'),

    # Classgroup 
    path('class/', ClassGroup.ClassGroupListView.as_view(), name='class-list'),
    path('class/new/', ClassGroup.ClassGroupCreateView.as_view(), name='class-add'),
    path('class/<pk>/edit/', ClassGroup.ClassGroupEditView.as_view(), name='class-edit'),
    path('class/<pk>/assign/', ClassGroup.ClassGroupAssignView.as_view(), name='class-assign'),
    path('class/<pk>/delete/', ClassGroup.ClassGroupDeleteView.as_view(), name='class-delete'),
    path('delete_child_group', ClassGroup.delete_child_group, name="delete_child_group"),
    path('classchilds/<pk>/', ClassGroup.childs_groups, name='class-child'),
    path('classgallery/<pk>/', ClassGroup.gallery_class, name='class-gallery'),
    path('classgallery/<pk>/new/', Gallery.GalleryCreateView.as_view(), name='gallery-add'),    
    path('dailyChild/', AssistanceDaily.save_daily_child, name='save_daily_child'),    

    # Alert
    path('alert/', Alert.AlertListView.as_view(), name='alert-list'),
    path('alert/new/', Alert.AlertCreateView.as_view(), name='alert-add'),
    path('alert/<pk>/edit/', Alert.AlertEditView.as_view(), name='alert-edit'),
    path('alert/<pk>/delete/', Alert.AlertDeleteView.as_view(), name='alert-delete'),
    path('get_alerts', Alert.get_alerts, name="get_alerts"),
    
    # Activity 
    path('activity/', Activity.ActivityListView.as_view(), name='activity-list'),
    path('activity/new/', Activity.ActivityCreateView.as_view(), name='activity-add'),
    path('activity/<pk>/edit/', Activity.ActivityEditView.as_view(), name='activity-edit'),
    path('activity/<pk>/assign/', Activity.ActivityAssignView.as_view(), name='activity-assign'),
    path('activity/<pk>/delete/', Activity.ActivityDeleteView.as_view(), name='activity-delete'),
    path('delete_child_activity', Activity.delete_child_activity, name="delete_child_activity"),
    path('activitychilds/<pk>/', Activity.childs_groups, name='activity-child'),
    
    # AsssitanceDaily    
    path('daily_child/', AssistanceDaily.AssistanceDailyChildListView.as_view(), name='daily-child'),
    path('daily_professor/', AssistanceDaily.AssistanceDailyProfessorListView.as_view(), name='daily-professor'),

    #Password 

]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL,document_root=settings.MEDIA_ROOT)