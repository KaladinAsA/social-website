from django.test import TestCase
from django.contrib.auth import get_user_model
from .models import Profile, Contact

User = get_user_model()

class ProfileModelTest(TestCase):

    def setUp(self):
        # test user
        self.user = User.objects.create_user(
            username='testuser', password='testpassword'
        )

    def test_profile_creation(self):
        # Ensure the Profile is automatically created for the user
        profile = Profile.objects.create(user=self.user, date_of_birth='1990-01-01')
        self.assertEqual(profile.user, self.user)
        self.assertEqual(str(profile), f'Profile of {self.user.username}')

    def test_profile_optional_fields(self):
        # Test that photo and date_of_birth are optional
        profile = Profile.objects.create(user=self.user)
        self.assertIsNone(profile.date_of_birth)
        self.assertFalse(profile.photo)

class ContactModelTest(TestCase):

    def setUp(self):
        # Create test users
        self.user1 = User.objects.create_user(
            username='user1', password='password1'
        )
        self.user2 = User.objects.create_user(
            username='user2', password='password2'
        )
        self.user3 = User.objects.create_user(
            username='user3', password='password3'
        )

    def test_contact_creation(self):
        # Test creating a Contact
        contact = Contact.objects.create(user_from=self.user1, user_to=self.user2)
        self.assertEqual(str(contact), f'{self.user1} follows {self.user2}')
        self.assertIn(contact, Contact.objects.all())

    def test_following_relationship(self):
        # Test the following/followers relationship
        Contact.objects.create(user_from=self.user1, user_to=self.user2)
        Contact.objects.create(user_from=self.user1, user_to=self.user3)

        self.assertIn(self.user2, self.user1.following.all())  # user1 follows user2
        self.assertIn(self.user3, self.user1.following.all())  # user1 follows user3

        self.assertIn(self.user1, self.user2.followers.all())  # user2 is followed by user1
        self.assertIn(self.user1, self.user3.followers.all())  # user3 is followed by user1

    def test_followers_and_following_counts(self):
        # Test counts for followers and following
        Contact.objects.create(user_from=self.user1, user_to=self.user2)
        Contact.objects.create(user_from=self.user2, user_to=self.user3)

        self.assertEqual(self.user1.following.count(), 1)  # user1 follows 1 person
        self.assertEqual(self.user2.following.count(), 1)  # user2 follows 1 person
        self.assertEqual(self.user2.followers.count(), 1)  # user2 is followed by 1 person
        self.assertEqual(self.user3.followers.count(), 1)  # user3 is followed by 1 person
