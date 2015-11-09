from django.shortcuts import render
from shaker.shaker_core import *
from django.http import HttpResponseRedirect


def shell_runcmd(request):
    sapi = SaltAPI()
    #host = sapi.runner_status("up")
    if request.POST:
        cmd = request.POST.get("cmd")
        host_list = request.POST.getlist("host")
        host_str = ",".join(host_list)
        result = sapi.shell_remote_execution(host_str,cmd)
        return render(request,'execute/minions_shell_runcmd.html', {'result': result })
    host = ["a","b","c","d","e","f"]
    return render(request,'execute/minions_shell_runcmd.html',{'host': host })
    #return HttpResponseRedirect('minions_shell_runcmd.html')


def salt_runcmd(request):
    return render(request,'execute/minions_salt_runcmd.html',)
