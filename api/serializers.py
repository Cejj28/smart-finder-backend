from rest_framework import serializers
from django.contrib.auth.models import User
from .models import Item, UserProfile, Claim, Notification

class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ('id', 'username', 'email', 'password', 'is_staff', 'is_active')
        extra_kwargs = {'password': {'write_only': True}}

    def create(self, validated_data):
        user = User.objects.create_user(
            username=validated_data['username'],
            email=validated_data.get('email', ''),
            password=validated_data['password'],
            is_staff=validated_data.get('is_staff', False),
            is_active=validated_data.get('is_active', True)
        )
        return user

class StudentRegisterSerializer(serializers.Serializer):
    full_name = serializers.CharField(max_length=255)
    email = serializers.EmailField()
    department = serializers.CharField(max_length=255)
    password = serializers.CharField(write_only=True, min_length=6)
    confirm_password = serializers.CharField(write_only=True)

    def validate_email(self, value):
        if User.objects.filter(email=value).exists():
            raise serializers.ValidationError("An account with this email already exists.")
        return value

    def validate(self, data):
        if data['password'] != data['confirm_password']:
            raise serializers.ValidationError({"confirm_password": "Passwords do not match."})
        return data

    def create(self, validated_data):
        email = validated_data['email']
        # Auto-generate username from the email prefix, ensure uniqueness
        base_username = email.split('@')[0]
        username = base_username
        counter = 1
        while User.objects.filter(username=username).exists():
            username = f"{base_username}{counter}"
            counter += 1

        user = User.objects.create_user(
            username=username,
            email=email,
            password=validated_data['password'],
            first_name=validated_data['full_name'].split(' ')[0],
            last_name=' '.join(validated_data['full_name'].split(' ')[1:]),
            is_staff=False,  # Students can never access the admin website
        )
        # Update the profile created by the signal
        profile = user.profile
        profile.full_name = validated_data['full_name']
        profile.department = validated_data['department']
        profile.role = 'student'
        profile.save()

        return user

class ItemSerializer(serializers.ModelSerializer):
    reporter_username = serializers.ReadOnlyField(source='reporter.username')

    class Meta:
        model = Item
        fields = '__all__'
        read_only_fields = ('reporter', 'created_at')

class ClaimSerializer(serializers.ModelSerializer):
    item_name = serializers.ReadOnlyField(source='item.item_name')
    claimant_username = serializers.SerializerMethodField()

    class Meta:
        model = Claim
        fields = '__all__'
        read_only_fields = ('user', 'created_at')
        extra_kwargs = {
            'claimant_name': {'required': False, 'allow_blank': True}
        }

    def get_claimant_username(self, obj):
        return obj.user.username if obj.user else None

class NotificationSerializer(serializers.ModelSerializer):
    class Meta:
        model = Notification
        fields = '__all__'
        read_only_fields = ('user', 'created_at')

class UserProfileSerializer(serializers.ModelSerializer):
    full_name = serializers.CharField(source='profile.full_name', allow_blank=True)
    department = serializers.CharField(source='profile.department', allow_blank=True)
    role = serializers.CharField(source='profile.role', read_only=True)

    class Meta:
        model = User
        fields = ('id', 'username', 'email', 'full_name', 'department', 'role', 'is_staff')
        read_only_fields = ('id', 'username', 'is_staff')

    def update(self, instance, validated_data):
        profile_data = validated_data.pop('profile', {})
        
        # Update User fields
        instance.email = validated_data.get('email', instance.email)
        instance.save()

        # Update UserProfile fields
        profile = instance.profile
        profile.full_name = profile_data.get('full_name', profile.full_name)
        profile.department = profile_data.get('department', profile.department)
        profile.save()

        return instance

class ChangePasswordSerializer(serializers.Serializer):
    current_password = serializers.CharField(required=True)
    new_password = serializers.CharField(required=True, min_length=6)
    confirm_password = serializers.CharField(required=True)

    def validate(self, data):
        if data['new_password'] != data['confirm_password']:
            raise serializers.ValidationError({"confirm_password": "New passwords do not match."})
        return data
