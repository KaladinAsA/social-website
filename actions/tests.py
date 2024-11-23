from django.test import TestCase
from django.contrib.auth.models import User
from django.contrib.contenttypes.models import ContentType
from .models import Action
from datetime import timedelta
from django.utils.timezone import now

class ActionModelTest(TestCase):
    def setUp(self):
        # Create a test user
        self.user = User.objects.create_user(username='testuser', password='password')

        # Create a test ContentType instance for the target
        self.content_type = ContentType.objects.get_for_model(User)

        # Create an Action instance
        self.action = Action.objects.create(
            user=self.user,
            verb="liked",
            target_ct=self.content_type,
            target_id=self.user.id
        )

    def test_action_creation(self):
        """Test that the action instance is created correctly."""
        self.assertEqual(Action.objects.count(), 1)
        action = Action.objects.first()
        self.assertEqual(action.user, self.user)
        self.assertEqual(action.verb, "liked")
        self.assertEqual(action.target_ct, self.content_type)
        self.assertEqual(action.target_id, self.user.id)

    def test_generic_foreign_key(self):
        """Test that the generic foreign key resolves correctly."""
        self.assertEqual(self.action.target, self.user)



    def test_ordering(self):
        """Test that the ordering is applied correctly."""
        # Create a second action with a slightly later timestamp
        action2 = Action.objects.create(
            user=self.user,
            verb="followed",
            target_ct=self.content_type,
            target_id=self.user.id
        )
        # Ensure action2 has a later timestamp
        action2.created = now() + timedelta(seconds=1)
        action2.save()

        actions = Action.objects.all()
        self.assertEqual(actions.first(), action2)  # Most recent action is first
        self.assertEqual(actions.last(), self.action)  # Oldest action is last

