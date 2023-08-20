# This is an auto-generated Django model module.
# You'll have to do the following manually to clean this up:
#   * Rearrange models' order
#   * Make sure each model has one field with primary_key=True
#   * Make sure each ForeignKey and OneToOneField has `on_delete` set to the desired behavior
#   * Remove `managed = False` lines if you wish to allow Django to create, modify, and delete the table
# Feel free to rename the models, but don't rename db_table values or field names.
from django.db import models

class CompInfo(models.Model):
    comp_uid = models.BigAutoField(primary_key=True)
    comp_name = models.CharField(unique=True, max_length=20)
    comp_loc = models.CharField(max_length=50)
    comp_thumb = models.CharField(max_length=2000, blank=True, null=True)
    comp_cont = models.CharField(max_length=30, blank=True, null=True)
    comp_founded = models.CharField(max_length=6, blank=True, null=True)
    comp_size = models.CharField(max_length=10, blank=True, null=True)
    comp_url = models.CharField(max_length=2000, blank=True, null=True)
    is_reged = models.CharField(max_length=1)
    create_date = models.CharField(max_length=8)
    modify_date = models.CharField(max_length=8)

    class Meta:
        managed = False
        db_table = 'comp_info'


class CompNews(models.Model):
    news_uid = models.BigAutoField(primary_key=True)
    comp_uid = models.ForeignKey(CompInfo, models.DO_NOTHING, db_column='comp_uid')
    pub_date = models.CharField(max_length=8)
    news_url = models.CharField(max_length=2000)
    news_cont = models.CharField(max_length=5000)
    news_sum = models.CharField(max_length=256, blank=True, null=True)
    news_senti = models.IntegerField(blank=True, null=True)
    create_date = models.CharField(max_length=8)
    modify_date = models.CharField(max_length=8)

    class Meta:
        managed = False
        db_table = 'comp_news'
