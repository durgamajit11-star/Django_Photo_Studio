from django.shortcuts import render

import recommendations

# Create your views here.
for rec in recommendations:
    rec.score = max(0, min(100, int(rec.score)))