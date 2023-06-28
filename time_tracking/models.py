from django.db import models

class TimeEntry(models.Model):
    user_id = models.IntegerField()
    task_id = models.IntegerField()
    work_date = models.DateField()
    entry_date = models.DateField()
    spent_time = models.CharField(max_length=50)
    task_title = models.CharField(max_length=500)
    project_title = models.CharField(max_length=500)
    user_full_name = models.CharField(max_length=500)
    task_status = models.CharField(max_length=500)