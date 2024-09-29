from rest_framework import serializers
from rest_framework.serializers import ValidationError

from .models import *


class UserSerializer(serializers.ModelSerializer):
    role = serializers.CharField(source='role.roles', read_only=True)

    class Meta:
        model = User
        fields = ['id', 'username', 'email', 'password', 'role']
        extra_kwargs = {'password': {'write_only': True},
                        "id": {"read_only": True},
                        "role": {"read_only": True}}


class PlayerSerializer(serializers.ModelSerializer):
    class Meta:
        model = Player
        fields = ['id', 'player_name']


class TeamSerializer(serializers.ModelSerializer):
    team_players = serializers.SerializerMethodField()

    class Meta:
        model = Team
        fields = ['id', 'team_name', 'team_players']

    def get_team_players(self, obj):
        players = obj.team_players.all()
        return [player.player_name for player in players]


class MatchSerializer(serializers.ModelSerializer):
    uploaded_by = serializers.CharField(source='uploaded_by.username',
                                        read_only=True)
    is_upcoming = serializers.SerializerMethodField()
    team1 = serializers.CharField(source="team1.team_name")
    team2 = serializers.CharField(source="team2.team_name")
    team1_players = serializers.PrimaryKeyRelatedField(queryset=Player.objects.all(), many=True)
    team2_players = serializers.PrimaryKeyRelatedField(queryset=Player.objects.all(), many=True)

    class Meta:
        model = Match
        fields = "__all__"

    def get_is_upcoming(self, obj):
        return obj.match_date > timezone.now().date()

    def to_representation(self, instance):
        representation = super().to_representation(instance)
        team1_players = representation.get('team1_players', [])
        team2_players = representation.get('team2_players', [])

        # Convert primary keys to player names
        team1_player_names = [player.player_name for player in Player.objects.filter(pk__in=team1_players)]
        team2_player_names = [player.player_name for player in Player.objects.filter(pk__in=team2_players)]

        representation['team1_players'] = team1_player_names
        representation['team2_players'] = team2_player_names

        return representation

    def validate(self, data):
        team1_players = data.get('team1_players')
        team2_players = data.get('team2_players')
        match_date = data.get('match_date')

        # Extract team names and other data directly from validated_data for update requests
        team1_name = data.get('team1').get('team_name') if 'team1' in data else None
        team2_name = data.get('team2').get('team_name') if 'team2' in data else None

        # Check if team names are provided
        if team1_name and team2_name:
            try:
                # Obtain team objects
                team1 = Team.objects.get(team_name=team1_name)
                team2 = Team.objects.get(team_name=team2_name)
            except Team.DoesNotExist:
                raise serializers.ValidationError("One of the teams does not exist.")

            # Obtain queryset of players for each team
            team1_players_queryset = Player.objects.filter(pk__in=[player.pk for player in team1_players], team=team1)
            team2_players_queryset = Player.objects.filter(pk__in=[player.pk for player in team2_players], team=team2)

            # Validate players
            if team1_players_queryset.count() != len(team1_players):
                raise serializers.ValidationError("One or more team1_players do not belong to team1")

            if team2_players_queryset.count() != len(team2_players):
                raise serializers.ValidationError("One or more team2_players do not belong to team2")

            instance = self.instance
            if instance is not None:
                # Exclude the current instance from the query
                existing_matches = Match.objects.exclude(pk=instance.pk).filter(match_date=match_date, team1=team1,
                                                                                team2=team2)
            else:
                existing_matches = Match.objects.filter(match_date=match_date, team1=team1, team2=team2)

            if existing_matches.exists():
                # If there are existing matches and it's not the instance being updated, raise validation error
                if instance is None or not existing_matches.filter(pk=instance.pk).exists():
                    raise serializers.ValidationError("A match with the same teams on the same date already exists.")

        return data

    def create(self, validated_data):
        user = self.context['request'].user
        print(user, "match user-------")
        team1_name_dict = validated_data.pop('team1')
        team2_name_dict = validated_data.pop('team2')
        team1_name = team1_name_dict.get('team_name')
        team2_name = team2_name_dict.get('team_name')
        try:
            if user.role.roles not in ['Streamer', 'Superadmin']:  # Check if user has appropriate role
                raise ValidationError("You are not authorized to create Matches")
        except Exception as e:
            raise ValidationError("An error occurred: {}".format(str(e)))

        try:
            team1 = Team.objects.get(team_name=team1_name)
        except Team.DoesNotExist:
            raise serializers.ValidationError("Team 1 does not exist.")

        try:
            team2 = Team.objects.get(team_name=team2_name)
        except Team.DoesNotExist:
            raise serializers.ValidationError("Team 2 does not exist.")

        validated_data['team1'] = team1
        validated_data['team2'] = team2
        validated_data['uploaded_by'] = user

        return super().create(validated_data)

    def update(self, instance, validated_data):
        user = self.context['request'].user
        # £Allow user with role streamer to update fields expect active field
        if user.role.roles in ["Streamer", "Superadmin"]:
            if user.role.roles == "Streamer":

                if instance.uploaded_by != user:
                    raise serializers.ValidationError("You are not author of this post")

                # "Check for show field in validate data"
                if "show" in validated_data:
                    raise serializers.ValidationError("Streamer not allowed to change the show field")
            elif user.role.roles == "Superadmin":
                instance.show = validated_data.get('show', instance.show)
            # Update basic fields
            instance.match_date = validated_data.get('match_date', instance.match_date)
            instance.location = validated_data.get('location', instance.location)

            # Update team1 if provided
            team1_data = validated_data.get('team1')
            if team1_data:
                team1_name = team1_data.get('team_name')
                try:
                    team1_instance = Team.objects.get(team_name=team1_name)
                    instance.team1 = team1_instance
                except Team.DoesNotExist:
                    raise serializers.ValidationError("Team 1 does not exist.")

            # Update team2 if provided
            team2_data = validated_data.get('team2')
            if team2_data:
                team2_name = team2_data.get('team_name')
                try:
                    team2_instance = Team.objects.get(team_name=team2_name)
                    instance.team2 = team2_instance
                except Team.DoesNotExist:
                    raise serializers.ValidationError("Team 2 does not exist.")

            # Update many-to-many relationships using .set() method
            if 'team1_players' in validated_data:
                instance.team1_players.set(validated_data['team1_players'])
            if 'team2_players' in validated_data:
                instance.team2_players.set(validated_data['team2_players'])

            instance.save()
            return instance
        else:
            raise serializers.ValidationError("NOT AUTHORIZED")


class MatchHighlightSerializer(serializers.ModelSerializer):
    match = serializers.PrimaryKeyRelatedField(queryset=Match.objects.all())
    highlight = serializers.FileField()
    testing = serializers.CharField(max_length=100)
    uploaded_by = serializers.CharField(source='uploaded_by.username',
                                        read_only=True)  # Use 'uploaded_by.username' to get the username
    like_count = serializers.SerializerMethodField()
    liked_by_user = serializers.SerializerMethodField()

    class Meta:
        model = MatchHighlight
        fields = ['id', 'match', 'uploaded_by', 'highlight', 'upload_date', 'active', 'testing',
                  'like_count', 'views', 'liked_by_user']

    def get_like_count(self, obj):
        return obj.liked_by_user.count()

    def get_liked_by_user(self, obj):
        liked_users = obj.liked_by_user.all()
        return [user.username for user in liked_users]

    def create(self, validated_data):
        user = self.context['request'].user
        highlight = validated_data['highlight']
        match = validated_data['match']
        testing = validated_data['testing']

        try:
            if user.role.roles not in ['Streamer', 'Superadmin']:  # Check if user has appropriate role
                raise ValidationError("You are not authorized to create highlights")
        except Exception as e:
            raise ValidationError("An error occurred: {}".format(str(e)))

        # Extract the primary key of the Match instance if it's an object
        if isinstance(match, Match):
            match_id = match.id
        else:
            match_id = match
        # Fetch the existing Match instance based on match_id
        try:
            match_instance = Match.objects.get(id=match_id)
        except Match.DoesNotExist:
            raise serializers.ValidationError("Invalid match_id")  # Handle if match_id is not found

        # Create and save the MatchHighlight instance
        instance = MatchHighlight.objects.create(
            match=match_instance,
            highlight=highlight,
            uploaded_by=user,
            testing=testing
        )

        # Automatically set upload_date and highlight_url and active
        instance.save()
        return instance

    def update(self, instance, validated_data):
        user = self.context['request'].user

        # Allow Streamer to update uploaded highlights fields except 'active'
        if user.role.roles == 'Streamer':

            if instance.uploaded_by != user:
                raise serializers.ValidationError("You are not author of this post")
            # Check if the 'active' field is present in validated_data
            if 'active' in validated_data:
                raise serializers.ValidationError("Streamers are not allowed to change the 'active' field")

            # Allow Streamer to update other fields
            instance.highlight = validated_data.get('highlight', instance.highlight)
            instance.testing = validated_data.get('testing', instance.testing)
            instance.save()
            return instance

        # Superadmin can update any field including 'active'
        elif user.role.roles == 'Superadmin':
            instance.highlight = validated_data.get('highlight', instance.highlight)
            instance.active = validated_data.get('active', instance.active)
            instance.testing = validated_data.get('testing', instance.testing)
            instance.save()
            return instance

        # Any other role is not allowed to update
        else:
            raise serializers.ValidationError("You don't have permission to perform this action")

    def to_representation(self, instance):
        request = self.context.get('request')
        if request and request.method == 'GET':
            # Check if the instance matches the requested primary key
            pk = request.parser_context['kwargs'].get('pk')
            if str(instance.pk) == pk:
                # Increment view count if it matches
                instance.views += 1
                instance.save()

        return super().to_representation(instance)
