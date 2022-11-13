from jobapp.models import Corporate, Job, Profile, User
from rest_framework import serializers

######################
# ---- USER ---- #
######################


class UserSerializer(serializers.ModelSerializer):

    class Meta:
        model = User
        fields = ('email',
                  'first_name',
                  'last_name',
                  'age',
                  'is_staff',
                  'is_active',
                  'date_joined',
                  )


class RegisterUserSerializer(serializers.ModelSerializer):
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
        user = User.objects.create_user(**validated_data)
        return user


class RegisterSerializer(serializers.ModelSerializer):
    password = serializers.CharField(max_length=50, min_length=4, write_only=True)
    email = serializers.EmailField(max_length=100)
    is_corporate = serializers.BooleanField(default=True)

    class Meta:
        model = User
        fields = ('email', 'password', 'is_corporate')

    def validate(self, attrs):
        email = attrs.get('email', '')
        if User.objects.filter(email=email).exists():
            raise serializers.ValidationError({'error': ('User already exist with this email')})
        return super().validate(attrs)

    def create(self, validated_data):
        user_type = validated_data.pop('is_corporate')
        user = User.objects.create_user(**validated_data)
        if user_type:
            corporate = Corporate()
            corporate.user = user
            corporate.save()
        else:
            profile = Profile()
            profile.user = user
            profile.save()
        return user


class LoginSerializer(serializers.ModelSerializer):
    password = serializers.CharField(max_length=50, min_length=4)
    email = serializers.EmailField(max_length=100)

    class Meta:
        model = User
        fields = ('email', 'password')
        read_only_fields = ('password', )


class TokenSerializer(serializers.Serializer):
    token = serializers.CharField(max_length=250)

######################
# ---- JOB ---- #
######################


class JobSerializer(serializers.ModelSerializer):

    class Meta:
        model = Job
        fields = '__all__'
        read_only_fields = ('total_interest', 'interested_users')


class JobInterestSerializer(serializers.Serializer):
    action_choices = [('add', 'Add to interest'), ('remove', 'Remove from interest')]
    action = serializers.ChoiceField(choices=action_choices)

######################
# ---- CORPORATE ---- #
######################


class CorporateSerializer(serializers.ModelSerializer):

    class Meta:
        model = Corporate
        fields = '__all__'


class CorporateWithUserSerializer(serializers.ModelSerializer):
    user = UserSerializer()

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


######################
# ---- PROFILE ---- #
######################


class ProfileSerializer(serializers.ModelSerializer):

    class Meta:
        model = Profile
        fields = '__all__'


class ProfileWithUserSerializer(serializers.ModelSerializer):
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


class JobsWithIntrestedProfileerializer(serializers.ModelSerializer):
    interested_users = ProfileWithUserSerializer(many=True, read_only=True)

    class Meta:
        model = Job
        fields = '__all__'
