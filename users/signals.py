from django.db.models.signals import post_save
#Django wuxuu leeyahay signal la yiraahdo post_save.
#Macnaheedu: "Marka object la save gareeyo kadib, samee wax kale."

from django.contrib.auth.models import User
#Waxaan isticmaaleynaa Django's default User.

from django.dispatch import receiver
#receiver wuxuu signal-ka ku xirayaa function-ka.

from .models import Profile
#Waxaan soo qaadaneynaa Profile-kii aan hadda sameynay


@receiver(post_save, sender=User)
#"Marka User cusub database-ka lagu save-gareeyo, function-kan shaqaysii."

def createUserProfile(sender, instance, created, **kwargs):
    #instance → user-ka hadda la sameeyay.
    #created → wuxuu sheegayaa user cusub yahay iyo in kale.

    if created:
        #Waxaan rabnaa user cusub oo keliya.
        Profile.objects.create(
            user=instance
        
        )
        #Profile-ka user-ka ayuu automatic u sameynayaa.
       #Role-ka ma siinayno, sidaas darteed model-ka ayaa isticmaalaya: