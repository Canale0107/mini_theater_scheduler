from django.shortcuts import render

# Create your views here.
import csv

def csv_view(request):
    with open('../../data/schedule_sample/all_schedule.csv', 'r') as csv_file:
        reader = csv.reader(csv_file)
        rows = [row for row in reader]

    context = {'rows': rows}
    return render(request, 'csv_template.html', context)


def test(request):
    return render(request, 'test.html')
