# -*- coding:utf-8 -*-
#!/bin/env python
import re

from django.shortcuts import render
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User

from shaker.shaker_core import *
from shaker.nodegroups import *
from groups.models import Groups,Hosts
from account.models import Businesses,Privileges,UserProfiles

@login_required(login_url="/account/login/")
def shell_runcmd(request):
    _u = request.user
    _user = User.objects.get(username=_u)

    _businesses = []
    all = {}
    try:
        if _user.is_superuser:
            _userprofile = UserProfiles.objects.all()
            _b = Businesses.objects.all()
        else:
            _userprofile = UserProfiles.objects.get(user=_user)
            _b = _userprofile.business.all()
        for _tmp in _b:
            _businesses.append(_tmp.name)

        _groups=Groups.objects.filter(business__in = _businesses)
        for _group in _groups:
            _h=[]
            _hosts=_group.groups_hosts_related.all()
            for _host in _hosts:
                _h.append(_host.minion.minion_id)
                all[_group.name]=_h
    except Exception as e:
        pass
    return render(request, 'execute/minions_shell_runcmd.html', {'list_groups': all})

@login_required(login_url="/account/login/")
def shell_result(request):
    sapi = SaltAPI()
    _u = request.user
    _user = User.objects.get(username=_u)
    host_list = request.POST.getlist("hosts_name")
    try:
        _userprofile = UserProfiles.objects.get(user=_user)
    except Exception as e:
        return render(request, 'execute/minions_shell_result.html')

    _privileges = _userprofile.privilege.all()

    _deny = []
    _allow = []

    line = "################################################################"
    result = {}
    minion_id_list = []
    
    for _p in _privileges:
        if len(_p.deny) > 0:
            _deny.append(_p.deny)  
        if len(_p.allow) > 0:
            _allow.append(_p.allow)

    if request.POST:
        cmd = request.POST.get("cmd").strip()
        if not _user.is_superuser:
            if _allow:
                _number = 0
                for _a in _allow:
                    _commands_split = _a.split(',')
                    for _cs in _commands_split:
                        _cmd_cs = _cs.strip('\'\"').split()
                        _cmd_cmd = cmd.strip().split()
                        _len_cs = len(''.join(_cmd_cs))
                        _len_cmd = len(''.join(_cmd_cmd))
                        if _len_cs == _len_cmd:
                           _compile = ""
                           for _tmp in _cmd_cs:
                               _compile = _compile + '.*' + str(_tmp)
                           _compile = _compile + '.*'
                           regex = re.compile(r''+_compile+'')
                           if regex.search(cmd) is not None:
                               _number = _number + 1
                if _number  <= 0 :
                    error = "error occurred : Allow Warn! You have no permition run [ " + cmd +" ]"
                    result["result"]=error
                    return render(request, 'execute/minions_shell_result.html', {'result': result, 'cmd': cmd, 'line': line})

            if _deny: 
                _number = 0
                for _a in _deny:
                    _commands_split = _a.split(',')
                    for _cs in _commands_split:
                        _cmd_cs = _cs.strip('\'\"').split()
                        _cmd_cmd = cmd.strip().split()
                        _len_cs = len(''.join(_cmd_cs))
                        _len_cmd = len(''.join(_cmd_cmd))
                        if _len_cs == _len_cmd:
                           _compile = ""
                           for _tmp in _cmd_cs:
                               _compile = _compile + '.*' + str(_tmp)
                           _compile = _compile + '.*'
                           regex = re.compile(r''+_compile+'')
                           if regex.search(cmd) is not None:
                               _number = _number + 1
                if _number >0:
                    error = "error occurred : Deny Warn! You have no permition run [ " + cmd +" ]"
                    result["result"]=error
                    return render(request, 'execute/minions_shell_result.html', {'result': result, 'cmd': cmd, 'line': line})
        else:
            pass

        for _h in host_list:
            try:
                _host = Hosts.objects.get(name=_h)
                minion_id_list.append(_host.minion.minion_id)
            except:
                minion_id_list.append(_h)
                        
        #run cmd now
        host_str = ",".join(minion_id_list)
        # the type of result is dictionary
        result = sapi.shell_remote_execution(host_str, cmd)
        return render(request, 'execute/minions_shell_result.html', {'result': result, 'cmd': cmd, 'line': line})
    return render(request, 'execute/minions_shell_result.html')

@login_required(login_url="/account/login/")
def salt_runcmd(request):
    return render(request, 'execute/minions_salt_runcmd.html')
