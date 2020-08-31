# Project Documentation: How to Compile, Configure, and Use Productivity Hub

## Compiling and Configuring Productivity Hub

To compile and configure Productivity Hub, first make sure that you cd into "todo", the folder containing all files for Productivity Hub.
Next, execute "flask run" in the terminal and click on the link that appears. The link will take you to the Welcome Page (index.html).

## Using Productivity Hub

### Welcome Page

The Welcome Page consists of a Navigation Bar, a "Register" option, and a "Login" option. The Navigation Bar consists of options for refreshing the welcome page,
registering, and logging in. By clicking on the "Register" button, you will be redirected the a Registration Page (register.html)
that will prompt you to enter a name, username, password, and password confirmation. Your password must be 8 characters long with at least 1 alphabetical letter and 1 number.
If you do not input a name, username, password, or password confirmation or you do not follow the password guidelines, an error message will appear. If you input all entries
correctly, you will be taken to the homepage of Productivity Hub. Similarly, if you click on the "Login" button, you will be taken to the Login Page (login.html), which
will require a username and password. If you input the correct username and password (i.e. usernames and passwords that exist in the database for the webpage), you will
also be taken to the homepage of Productivity Hub.

### Homepage

The Homepage consists of a greeting to the user (based on the username of their account) and also a prompt for the user to enter their daily focus. Additionally, now
that you are logged in, the Navigation Bar has more options, including Todo, List, Done, Study Group, Tips, Study Break, Calendar, Music, Settings, and Logout (more
on each those later). When you click on the icon to set your daily focus, you will be redirected to a Focus Page (focus.html) where you can set your daily focus.
Once you do so, you will be redirected to the Homepage where you will now see your daily focus below the words "Focus for the day:".

### Calendar Page

The Calendar Page consists of an embedded Google Calendar. The embed consists of two calendars: a Holidays Calendar and a Harvard Schedule Calendar. You can toggle back
and forth between the calendars and also see events from both simultaneously. This calendar is useful for planning your todo's; by knowing when holidays and Harvard
events occur, you can plan your list of todos accordingly around the holidays and Harvard Events.

### Todo Page

The Todo Page (todo.html) consists of a form that prompts you to input a todo. There are 3 fields that you must complete: Event, Priority, and Category. In Event, you must input
text; in Priority, you will select "High," "Med," or "Low" Priority; in Category, you will either input or select a category for your todo. In the event that you have
not created any todos, you will not be able to select a category; instead, you will have to click the "Add Category" button that will cause a "Category" input field to
appear. On the other hand, if you have already created a todo with a category, a "Categories" dropdown will appear and will allow you to select one of the categories
you have already entered. Additionally, you have the option of not entering a priority or a category. The priority will be set to "Low" by default and the category can
be NULL. Next, by clicking "Submit", you will be redirected to the List Page (list.html).

### List Page

The List Page (list.html) will contain a table that lists all of your todos. For each entry, the table will display the name of the todo, the date and time you created (or edited) the todo,
and the category of the todo. Each entry will also have a background color that indicated the priority of the todo; a pink background corresponds with high priority, a yellow
background corresponds with medium priority, and a light blue background corresponds with low priority. Each todo in the table will be grouped by priority, and then category.
Additionally, the List Page contains dropdown options for marking a todo as complete, editing a todo, and deleting a todo. Marking a todo as complete will take you to a form (completed.html
more on that later) and ultimately remove the todo from the List Page and instead display it in the History Page (history.html, more on that later). Editing a todo will redirect you to
another form (edit.html, more on that later) and ultimately update the todo that you selected in your List Page. Lastly, deleting a todo will remove it from the table in the List Page.

#### Complete Form

By clicking the "Mark as Complete" button in the List Page, you will be redirected to a form that prompts you to enter how much time (in minute) you spent on the todo, a rating from 1 to 10
on how you felt about completing your todo, and any additional comments you would like to enter about your todo. Upon completing this form, you will be redirected to the List Page, where
you will now notice that the todo you marked as complete is no longer in the table. However, by navigating to the History Page, you will see an entry for your completed todo.

#### History Page

The History Page consist of all of your completed todos. For each entry in the table, the date of completion, name, category, rating, reflection, and time spent on the todo will be displayed.
In addition, in the bottom row of the table, the number of todos that you completed will be displayed, along with the total amount of time (in minutes) that you have spent on all of your todos.
Lastly, there is a Delete dropdown option that allows you to delete todos from your history table. By selecting a todo and then clicking the delete button, you will be able to permanently
remove that todo from the history table.

#### Edit Form

By clicking the "Edit" button in the List Page, you will be redirected to a form that allows you to edit the priority and category of the todo that you selected. You may edit either or both the
priority and category of the todo. Upon pressing the "Submit" button, you will be redirected to the List Page, where you will notice that the todo you edited will now be updated with a new
priority and/or category.

### Study Group Page

The Study Group Page allows you to create a study group, join a study group, and view your study group (if you are part of one). Clicking on each of these three options will take you to
different forms, which are described below.


#### Creating a Group

When you click on "Make Group", you will be redirected to a page (groupmake.html) that prompts you to create a study group with a name and pin. You must input the name of your study group,
the pin for your study group, and a pin confirmation. After you input all of these values and hit "register group", you will be redirected to the Group View page (group.html) where you can
see the group you are a part of and the other members of the group (more on that later in "Viewing your Group").

#### Joining a Group

When you click on "Join Group", you will be redirected to the Join Group Page (groupjoin.html) that prompts you to join a study group. You must input the name of the study group you want
to join and the pin of the study group. After inputting the necessary information, you will be redirected to the Group View Page just like if you created your group.


#### Changing your Group

If you are already part of a group and would like to join a new group, you certainly can. However, you will change your group as a result because each user can only be part of one study
group. To change your group, simply fill out the Join Group form and your study group will be updated

#### Viewing your Group

Whenever you create a study group, join a study group, or click on the "View Group" button on the Study Group Page, you will be redirected to the View Group Page (groups.html) where you
will see a table of the other users who are also in the study group. The table only shows users who have completed todos. Each entry in the table will display the user's name, the number
of todos that the user has completed, and the total minutes that the user has spent on their completed todos. Additionally, you will be able to see the name of the study group that you
are a part of in the upper left hand corner of the page.

### Music Page

The Music Page consists of embedded Spotify playlists that allows you to listen to music while you work or take a break. There is a spotify button that, which clicked, causes other buttons
with different music genres to appear. By clicking one of those buttons, an embedded Spotify playlist of that genre will appear, and now you can click play on the playlist to play some
music. Clicking on the other buttons will switch the playlist that appears on the screen. This way, you can easily change the genres of music that you wish to play.

### Tips Page

The Tips Page consists of a dropdown that allows you to select different categories of tips. There are five categories (Goal Setting, Timing and Time Management, Managing Your Schedule,
Completing To'Do's, and Sleep), and by selecting different categories, you can toggle between different tips for managing your tasks and increasing your productivity.

### Study Break Page

The Study Break Page contains a dinosaur game that allows you to take a break from working and relax. To start the game, press the spacebar. Upon losing the game, your score will be recorded.
There are also sound effects for jumping over an obstacle, reaching a certain score, and losing the game.

### Settings Page

The Settings Page contains options for you to change your Avatar and also the appearance of snow on the homepage. To toggle the appearance of snow in the homepage, select whether you want
snow or no snow, and then click the "Update Settings" button underneath the options. If you opted for snow, you can go back to the homepage and now see that there are snowflakes falling from
the top of the screen. To toggle your Avatar in the homepage, select whether you want a tree, the Harvard Coat of Arms, or David Malan as your Avatar in the dropdown. Then, select
"Update Settings" underneath the dropdown, and the page will refresh. When you navigate to the homepage, you will now notice that your avatar has changed to the avatar that was selected.