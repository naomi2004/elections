from voting.models import PollingCenter

batch_size = 500
while True:
    centers = PollingCenter.objects.all()[:batch_size]
    if not centers:
        break
    centers.delete()
print('All polling centers deleted.') 