from coreapp.models import UserIP

# class RequestMiddleware:
#     def __init__(self, get_response):
#         self.get_response = get_response

#     def __call__(self, request):
#         ip_address = request.META.get('REMOTE_ADDR')
#         if request.user.is_authenticated:
#             UserIP.objects.create(user=request.user, ip_address=ip_address)
#         response = self.get_response(request)
#         return response


from coreapp.models import UserIP

class RequestMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        ip_address = request.META.get('REMOTE_ADDR')
        if request.user.is_authenticated:
            user_ips = UserIP.objects.filter(user=request.user, ip_address=ip_address)
            if user_ips.exists():
                # Update the timestamp of the first instance
                user_ip = user_ips.first()
                user_ip.save()
            else:
                # Create a new instance if no instance exists with the same user and IP address
                user_ip = UserIP.objects.create(user=request.user, ip_address=ip_address)
        response = self.get_response(request)
        return response


