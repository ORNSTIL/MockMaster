365 User Stories and Exceptions
MockMaster
Alex Vasquez
Xavier Garcia
Sam Todd
Luca Ornstil

User Stories
1. As a fantasy football enthusiast, I want to be able to choose a draft room which matches my experience level.
2. As a fantasy football analyst, I want to access detailed player statistics and history during the draft, so that I can make informed decisions.
3. As a user interested in different fantasy league formats, I want to be able to create different types of drafts (PPR, .5 PPR, non-PPR) so I can practice in drafts that align with my interests.
4. As a user interested in different fantasy league formats, I want to be able to join different types of drafts (PPR, .5 PPR, non-PPR) so I can practice in drafts that align with my interests.
5. As a user interested in participating in different fantasy leagues, I want to be able to create different types of drafts (public or private) so I can practice in drafts that align with my interests.
6. As a user interested in participating in different fantasy leagues, I want to be able to join different types of drafts (public or private) so I can practice in drafts that align with my interests.
7. As a fantasy football veteran, I want to be able to customize the draft settings, such as draft length and roster positions, to simulate various league formats and challenges.
8. As a fantasy football commissioner, I want the ability to pause the mock draft in case special circumstances arise, allowing the group to resume the draft at a later time.
9. As a fantasy football enthusiast with a busy schedule, I want the ability to participate in mock drafts at any time, whether it's through scheduled sessions or on-demand drafts, accommodating different time zones and availability.
10. As a fantasy football competitor, I want the option to save and analyze past mock drafts, helping me improve my drafting skills over time.
11. As a busy/distracted individual, I want a player that meets my needs to be automatically drafted to my team if I miss my turn during the draft.
12. As someone with limited free time, I want to be able to quickly draft on my own, against the computer so that I do not have to wait for other individuals to make their selections.

Exceptions/Error Scenarios
1. User login failure
  a. If a user enters incorrect login credentials, the system will display an error message indicating to try entering their information again.
2. Internet issues during draft
  a. If a user experiences a loss of internet during a draft, the system will attempt to reconnect and save the draft progress up to the last action. The user will also     receive a notification of their connection status.
3. Player pick time expires
  a. If a user fails to pick a player within their allotted time, the system will automatically draft a player based on the highest ranking player available, or the highest ranked player on a user’s pre-draft preference list. The user will be notified of the automatic selection. 
4. Technical issues with accessing player information
  a. If there are technical difficulties or server issues that prevent users from accessing the list of available players and history during the draft, the system will display a message informing users of the problem and advising them to try accessing the information again later. 
5. Draft creation failure
  a. If a user encounters an error when attempting to create a custom draft with specific settings (such as draft type or roster positions), the system will display an error message indicating the issue and providing guidance on possible solutions. 
  b. This could include suggesting alternative draft settings or advising the user to try again later. 
6. Draft join failure
  a. If a user encounters an error when attempting to join a public draft, the system will display an error prompting the user to try again.
7. Custom draft join failure
  a. If a user enters the incorrect credentials to join a private draft, the system should display a message explaining that invalid credentials were entered, prompting the user to double check the fields they entered.
8. Draft saving failure
  a. If there is a problem with saving and analyzing past mock drafts, such as data not being properly recorded or accessible, the system will display an error message indicating the issue and advising users to try accessing their draft history again later. 
9. Inappropriate draft room assignment
  a. If a fantasy football enthusiast is assigned to a draft room that does not match their experience level (e.g., a novice player assigned to an advanced draft room), the system will detect the mismatch and prompt the user to confirm their selection or suggest a more suitable draft room based on their experience level.
10. Invalid draft selection
  a. If a user attempts to select a player which would violate the draft settings (e.g. the user tries to draft a 5th running back when the draft settings dictate a maximum of 4 running backs per team), the system will not allow the user to select the player and will display a message informing the user that they cannot select any more players of that position.
11. Technical issues with computer draft opponent
  a. If a user encounters technical difficulties while participating in a draft against the computer opponent, such as delays or freezing during the draft process, the system will display a message informing the user of the issue and advise them to refresh the page or try again later.
12. Invalid attempt to join a draft
  a. If a user is currently in a draft and attempts to join another draft (or the same draft again), the system will not allow the user to join any other draft while the current draft is active.
  b. If the user wishes to join another draft, they may leave the draft that they are in (prompting a computer player to take their place) and join another draft.

