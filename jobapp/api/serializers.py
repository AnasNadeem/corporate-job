from jobapp.models import Corporate, Job, Profile, User
from rest_framework import serializers


class UserSerializer(serializers.ModelSerializer):

    class Meta:
        model = User
        fields = ('email',
                  'first_name',
                  'last_name',
                  'phone_number',
                  'is_staff',
                  'is_active',
                  'date_joined',
                  )


class RegisterSerializer(serializers.ModelSerializer):
    password = serializers.CharField(max_length=50, min_length=4, write_only=True)
    email = serializers.EmailField(max_length=100)

    class Meta:
        model = User
        fields = ('email', 'password')

    def validate(self, attrs):
        email = attrs.get('email', '')
        if User.objects.filter(email=email).exists():
            raise serializers.ValidationError({'error': ('User already exist with this email')})
        return super().validate(attrs)

    def create(self, validated_data):
        user_type = validated_data.pop('type')
        user = User.objects.create_user(**validated_data)
        if user_type == 'seeker':
            profile = Profile()
            profile.user = user
            profile.save()
        return user


class JobSerializer(serializers.ModelSerializer):

    class Meta:
        model = Job
        fields = '__all__'
        depth = 1


class CorporateSerializer(serializers.ModelSerializer):

    class Meta:
        model = Corporate
        fields = '__all__'


class CorporateWithJobSerializer(serializers.ModelSerializer):
    corporate_jobs = serializers.SerializerMethodField()
    user = UserSerializer()

    class Meta:
        model = Corporate
        fields = (
            'id',
            'user',
            'description',
            'corporate_jobs',
        )

    def get_corporate_jobs(self, obj):
        corporate = Corporate.objects.get(pk=obj.id)
        jobs = corporate.job_set.all()
        jobs_serializer = JobSerializer(jobs, many=True)
        return jobs_serializer.data


class ProfileSerializer(serializers.ModelSerializer):
    user = UserSerializer()

    class Meta:
        model = Profile
        fields = '__all__'


# class JobWithUserInterestSerializer(serializers.ModelSerializer):
#     corporate = CorporateSerializer()

#     class Meta:
#         model = Job
#         fields = (
#             'id',
#             'corporate',
#             'title',
#             'description',
#             'total_interest',
#         )
