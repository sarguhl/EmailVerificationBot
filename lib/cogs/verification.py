import smtplib
import random
import discord
from discord.ext import commands
from discord.utils import get
import re

"""
// IMPORTANT: You may have to read the SMTP-Documentation (for python) in order to understand a few parts in the following code.
// Also, this code is not optimised, so if you might want to add stuff for your own, go a head. But would be cool if you could let me know!
// So I can adapt it to my own code ;)
// Best of luck, Sarguhl
// Here's a link to the SMTP-docs: https://docs.python.org/3/library/smtplib.html
"""

# SUMMARY: the variable below contains the password for your email.
smtpPassword = "Password"
USERS = []

# SUMMARY: The following 3 variables are used to generate the Pass-Code later on in the code. It contains the number 6 two times to make a higher chance of letting it appear in the code.
numbers = "1234566789"
all = numbers
length = 6

# SUMMARY: This is the email you want to be your code send from.
sender = "your-verify@email.here"

# SUMMARY: Just error handling, ignore it.
class SMTPException(smtplib.SMTPException):
    pass

class VerificationProcess(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
    
    # SUMMARY: Just for logging :)
    @commands.Cog.listener()
    async def on_ready(self):
        if not self.bot.ready:
            self.bot.cogs_ready.ready_up("reactions")
    
    """
    // Now here comes the main part.
    // The concept is the following:
    // If a member joins the server, the bot automatically DMs the user and give it role.
    // It asks for the user's email. In case this fails, the bot'll kick the member.
    // When the verification had success, the bot'll automatically give and remove a role from the user.
    """
    @commands.Cog.listener()
    async def on_member_join(self, member):
        guild = member.guild
        unver_role = get(guild.roles, id=809476969007677528) # <- this will be the ID of the role a user will receive when joining the server.
        ver_role = get(guild.roles, id=809465281574469633) # <- and this is the role the user will receive after the verification process.
        
        await member.add_roles(unver_role) # Add's the unverified role.
        
        await member.send("Hello, please give me your email to send you a verification code.") # This message will be sent to the user in DMs.
        
        msg = await self.bot.wait_for('message', check=lambda message: message.author == member) # Waits for a message from the user.
        if re.match("([a-zA-Z0-9_.+-]+@college-mail.com)", msg.content) is not None: # After the @ sign in the string, put the url of your college email.
            """
            // The following code will check for the student email.
            // So an example would be: my-name@sarguhl.lol
            // or: teachers@waldorfschule-detmold.de
            """
            reveivers = [msg.content] # Defines the receivers.
            password = "".join(random.sample(all, length)) # Generates the verify-code.
                                                                # add Email here
            message = f"""From: Discord Collage Verification <your-verify@email.here>
To: {member.display_name} <{msg.content}>
Subject: Discord College Verification
=======
Hello there!
Your verification code is the following: """ + password + """
Now please paste it in our private chat.
Best,
Your Name
""" # This is the email-content that'll be sent to the user.
        
            try:                                            
                smtpObj = smtplib.SMTP('your-email-server.com', 587) # This is the domain of your email server.
                smtpObj.ehlo()
                smtpObj.starttls()
                smtpObj.ehlo()
                smtpObj.login(sender, smtpPassword)
                smtpObj.sendmail(sender, reveivers, message)
                smtpObj.quit()
                await member.send("Please check your email-inbox!")
            except SMTPException:
                await member.send("I'm sorry, but I couldn't find this email. Please contact an administator.")
            
            msg2 = await self.bot.wait_for('message', check=lambda message: message.author == member) # Waits for the verification code.

            if msg2.content == password: # Checks if the message is equal to the code. (can be optimised tho...)
                await member.add_roles(ver_role) # <- adds the verify-role.
                await member.remove_roles(unver_role) # <- removes the unverified role.
                
                await member.send("Great, you're verified now! Please have a look at the server.")
            
            else:
                # SUMMARY: The following code just sends an error message to the user and then kicks it.
                await member.send("Hm, seems to be your verification code was not correct. In order to redo the verification, rejoin the server.")
                await member.kick(reason="Verification failed at: Entering the code.")
        else:
            # SUMMARY: The following code just sends an error message to the user and then kicks it.
            await member.send("Hm, seems like your email wasn't correct. In order to redo the verification, rejoin the server.")
            await member.kick(reason="Verification failed at: Entering the emai.")
    
def setup(bot):
    bot.add_cog(VerificationProcess(bot))