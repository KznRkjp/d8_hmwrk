from django.db.models.signals import m2m_changed, post_save, post_delete, pre_save
from django.dispatch import receiver
from tasks.models import TodoItem, Category, PriorityCount
from collections import Counter


@receiver(m2m_changed, sender=TodoItem.category.through)
def task_cats_added(sender, instance, action, model, **kwargs):
    if action != "post_add":
        return

    for cat in instance.category.all():
        slug = cat.slug

        new_count = 0
        for task in TodoItem.objects.all():
            new_count += task.category.filter(slug=slug).count()

        Category.objects.filter(slug=slug).update(todos_count=new_count)


@receiver(m2m_changed, sender=TodoItem.category.through)
def task_cats_removed(sender, instance, action, model, **kwargs):
    if action != "post_remove":
        return

    cat_counter = Counter()
    for t in TodoItem.objects.all():
        for cat in t.category.all():
            cat_counter[cat.slug] += 1

    for slug, new_count in cat_counter.items():
        Category.objects.filter(slug=slug).update(todos_count=new_count)

# @receiver(post_save, sender=TodoItem)
# def task_created(instance, **kwargs):
#     print(kwargs)
#     if PriorityCount.objects.filter(name = instance.get_priority_display()):
#         k = PriorityCount.objects.get(name = instance.get_priority_display())
#         k.prior_count+=1
#         k.save()
#     else:
#         k = PriorityCount()
#         k.name = instance.get_priority_display()
#         k.prior_count = 1
#         k.save()

@receiver(pre_save, sender=TodoItem)
def task_edited(instance, **kwargs):
    if instance.id:
        old_priority = TodoItem.objects.get(pk=instance.id)
        k = PriorityCount.objects.get(name = old_priority.get_priority_display())
        k.prior_count-=1
        k.save()
        if PriorityCount.objects.filter(name = instance.get_priority_display()):
            k = PriorityCount.objects.get(name = instance.get_priority_display())
            k.prior_count+=1
            k.save()
        else:
            k = PriorityCount()
            k.name = instance.get_priority_display()
            k.prior_count = 1
            k.save()
    else:
        if PriorityCount.objects.filter(name = instance.get_priority_display()):
            k = PriorityCount.objects.get(name = instance.get_priority_display())
            k.prior_count+=1
            k.save()
        else:
            k = PriorityCount()
            k.name = instance.get_priority_display()
            k.prior_count = 1
            k.save()


@receiver(post_delete, sender=TodoItem)
def task_deleted(instance, **kwargs):
    if PriorityCount.objects.filter(name = instance.get_priority_display()):
        k = PriorityCount.objects.get(name = instance.get_priority_display())
        if k.prior_count > 0:
            k.prior_count-=1
            k.save()
        else:
            pass
    else:
        pass
