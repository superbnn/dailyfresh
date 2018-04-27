from django.contrib.auth.decorators import login_required
from django.views.generic import View



class BaseView(View):
    pass

class LoginRequiredView(View):


    # 为什么要声明为类方法？内部限制，少一个参数
    @classmethod
    def as_view(cls, **initkwargs):
        view_fun = super().as_view(**initkwargs)
        view_fun = login_required(view_fun)
        return view_fun


class LoginRequiredMixin(object):
    '''检测用户是否登录'''

    @classmethod
    def as_view(cls, **initkwargs):
        view_fun = super().as_view(**initkwargs)
        view_fun = login_required(view_fun)
        return view_fun
