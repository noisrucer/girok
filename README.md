contents

1. Girok Intro
2. Version Info
3. Table of contents
   1. Installation
   2. Commands
      1. `--help`
      2. Auth
      3. Category
      4. Task
      5. Calendar
   3. Use cases
   4. Major Updates Plan
   5. Troubleshooting
   6. Uninstall
   7. Contributions

<h1 align="center">✏️ Girok - The most powerful CLI task manager</h1>

<h3 align="center"> Who said you cannot have a beautiful UI on terminal?</h4>

Girok is a **powerful terminal-based task manager** which provides a multitude of scheduling operations that can be done in less than 10 seconds. It also supports **beautiful and responsive calendar GUI** in which you can move around with VIM key bindings.

Girok is running on AWS server so you can **login from any device in the world**!

# 📀 Version `0.1.6` is released now!

### Upgrade with `pip install girok --upgrade`

# 📖 Table of Contents

- [🚀 Installation](#-Installation)
- [🔥 Get Started](#-get-started)
  - [1. help command](#help-command)
  - [2. Register](#register)
  - [3. Login / Logout](#login-and-logout)
  - [4. Category commands](#category-commands)
  - [5. Task Commands](#task-commands)
  - [6. Calendar Commands](#calendar-commands)
- [📝 Use cases](#-use-cases)
- [🤖 Major updates plan](#-major-updates-plan)
- [🚒 Troubleshooting](#-troubleshooting)
- [😭 Uninstall](#-uninstall)
- [💌 Contributions](#-contributions)

# 🚀 Installation

Girok supports all operating systems including Linux, MacOS, Windows.

However, it works well on linux-based shells such as `bash`, `zsh`, `fish`, `git-bash`, etc.

Some shells like `powershell` might break some UIs.

1. Make sure you have Python `>3.9` version installed.
2. Enter the following in your terminal

```bash
pip install girok
```

Now you have installed `girok` on your machine. To make sure that it works, enter the following.

```bash
girok --help
```

Now, let's dive into Girok!

# 🔥 Get Started

## 1. Help command

In order to see **all the commands** of **Girok**, enter `girok --help` in your terminal.

![](images/girok-help.png)

In order to see the details of each command, enter the following in your terminal.

```
girok <command> --help
```

For example, if you enter

```
girok addtask --help
```

then you'll see the following help message

![](images/girok-command-help.png)

## 2. Register

To register a new account enter the following in your terminal.

```bash
girok register
```

![](images/girok-register.png)

Congratulations! Now let's go ahead and login to our account.

## 3. Login and Logout

In order to login with your registered account, enter the following command.

```bash
girok login
```

![](images/girok-login.png)

Now you're ready to use all the features.

## 4. Category Commands

You can pre-define **categories** such as `School`, `Life` and `Career` with automatically assigned category color.

Girok supports **infinite recursive subcategories**. All the subcategories will be assigned with the color of its topmost parent category.

Later on, you can link tasks to these categories.

### 4.1 `showcat` command

In order to see all the categories you have created, enter the following command.

By default, `No Category` category is set (later for tasks which have no category).

```bash
girok showcat
```

![](images/girok-addcat3.png)

### 4.2 `addcat` command

`addtask` command takes a single argument `category full path`.

In order to add a new category, enter the following command.

```bash
girok addcat <target path>
```

The `<target path>` is the **full path including the new category name**. For example, if you want to add a **topmost category** named `Career`, then enter

```bash
girok addcat Career
```

Then, you'll see the category tree with the newly created category being highlighted.

![](images/girok-addcat1.png)

In order to nest a sub-category under a previously defined category, pass the **FULL PATH** starting from the topmost category delimited by `/`, ending with the new category name.

For example, if you want to create a new category named `Resume` under the previously created `Career` category, enter the following command.

```bash
girok addcat Career/Resume
```

Then, you'll see `Resume` is created under `Career`.

![](images/girok-addcat2.png)

In this way, you can create as many categories and sub-categories as you want!

### 4.3 `mvcat` command

Now you might want to move a category under another category.

In order to move a `category A` (recursively all its sub-categories) under `category B`, enter the following command.

```bash
girok mvcat <full path of A> <full path of B>
```

For example, if you want to move the whole `Career` category under `Dev/Network` (for some weird reason), enter the following command.

```bash
girok mvcat Career Dev/Network
```

![](images/girok-addcat4.png)

If you want to move a category to the `root category`, then pass `/` as the second argument. Let's move `Dev/Network/Career` back to the topmost category.

```bash
girok mvcat Dev/Network/Career /
```

![](images/girok-addcat5.png)

### 4.4 `rmcat` command

Of course, you want to delete a category. In that case, enter the following command.

```bash
girok rmcat <full path of category>
```

Let's add a dummy category named `Dummy` under `Dev` then remove it.

As you already know, enter

```bash
git addcat Career/Dummy
```

![](images/girok-addcat6.png)

Now, let's delete it with the following command.

**[WARNING]** If you delete a category, **all its sub-categories and tasks will be DELETED**. I'll consider adding an option for users to preserve all the orphan tasks in the future. Please let me know in the issue if you need this feature!

```bash
girok rmcat Career/Dummy
```

Then, you'll be asked to confirm the deletion. Enter `y`.

![](images/girok-rmcat1.png)

Great job! Now let's move on to the task commands.

## 5. Task commands

**Girok** provides powerful task scheduling operations. You can perform different operations that would've taken in other schedulers like Notion and Google Calendar in less than 10 seconds (If you get used to the commands).

### 5.1 `addtask` command

```bash
girok addtask <task name> [One of deadline date options] [-c | --category <category path>] [-p | --priority <priority>] [-t | --time <deadline time>] [-T | --tag <tag name>]
```

It looks quite complicated but don't worry! Let's go through some rules.

#### 5.1.1 `addtask` rules

1. `<task name>` (Argument / **Required**) - If the task name has no space you can omit double quotes `""`. If it does, enclose the task name by double quotes `""`
2. `<One of date options>` (Option / **required**) - You must specify a **deadline "date"** of a task. There're many ways to add a deadline. Note that **ONLY ONE DATE OPTION** is allowed.
   - `-d <yyyy/mm/dd | mm/dd>`
     - Specify an exact date delimited by `/`. You can enter the full date in the form of `yyyy/mm/dd`. Or, you can omit the year like `mm/dd` then the deadline year will be set to the current year.
     - You don't have to enter the exact form filled with `0`s. If the month is May, then just enter `5/23` or `05/23`.
   - `-t1 ~ -t7 | --thismon ~ --thissun`
     - Sometimes, you're not aware of the exact date. If the date is some weekday of this week, you can just pass `-t{1-7}` referrting to this monday to this sunday (monday indexed as `0`).
     - For example, if the deadline is this friday, enter `girok addtask "dummy" -t5`
   - `-n1 ~ -n7 | --nextmon ~ --nextsun`
     - Similar to the above but referring to **next week**.
   - `-a <# days>`
     - Sometimes, you process the deadline in your mind like "it's due 5 days later".
     - In this case, pass the number of days a task is due after.
     - For example, if the deadline is 5 days later, enter `girok addtask "dummy" -a 5`
   - `--tdy`
     - Set the deadline to today.
   - `--tmr`
     - Set the deadline to tomorrow.
3. `-t | --time <hh:mm>` (Option, **Optional**) - You can also set the specific deadline time.
   - You must provide the full time format in **24 hour scale** such as `07:23` or `21:59`.
4. `-c | --category <category full path>` (Option / **Optional**) - Your tasks might belong to a specific category you have previously defined.
   - Provide the **full category path**.
   - For example, if your task belongs to `Career/Resume`, then enter `girok addtask "dummy task 1" --tmr -c Career/Resume`.
   - If you specify a category, then the task color will be automatically linked to that category's color.
   - If no category is provided, the task will belong to `No Category` category.
5. `-p | --priority <priority (1~5)>` (Option, **Optional**) - You can set the priority of a task so that you can filter out by priority when you query your tasks.
   - For example, to set the priority of a task as `5`, enter `girok addtask "dummy task 1" -c Career/Resume -p 5`.
6. `-T | --tag <tag name>` (Option, **Optional**) - You can set the **tag**(or type) of a task such as `assignment` and `meeting`. With tags, you can more efficiently query your tasks with different types.
   - Unlike category, tag doesn't allow nested tags and you don't have to pre-define them.
   - For example, if you want to set the tag of a task as `assignment`, enter `girok addtask "assignment 4" -c HKU/COMP3234 -d 4/24 --tag assignment`

In summary, keep the following rules in mind.

1. Always provide **task name** and **one of date options**.
2. Although not required, I think it's better to provide **category** to manage your tasks more effectively.
3. Other options are up to you!

For example, the following command is a typical command that I use on everyday basis.

```bash
girok addtask "Implement tag filtering feature" -c Dev/Girok -a 3 -p 5
```

It looks quite complicated, but you'll get used to it quickly after playing out little bit.

#### 5.1.2 `addtask` demonstration

Now let's play around with `addtask` command.

Recall our category list is

![](images/girok-addtask1.png)

In the demonstration, I will add several tasks and show how it works.

Let's add a task named `go over resume again` whose category is `Career/Resume` and I will do it by `next thursday`. This is a quite important task, so I will assign the `priority` of `5`.

```bash
girok addtask "go over resume again" -c Career/Resume -n4 -p 5
```

![](images/girok-addtask2.png)

When adding it, you will see the same category tree with tasks attached to the belonged category. (Priority is now shown by default. You can see the priority with `girok showtask` command we'll talk about very soon).

Now I'll add another task named `Midterm exam` with the category `HKU/COMP3234` and the deadline is `4/18 09:30`. Hmm.. I think I have plenty of time so I will not provide the priority. However, I will assign the tag `exam`.

```bash
girok addtask "Midterm exam" -c HKU/COMP3234 -d 4/18 -t 09:30 --tag exam
```

![](images/girok-addtask3.png)

Lastly, I'll add a task named `Hangout with Jason` and the appointment date is `tomorrow`. This time, I will not provide any option.

```bash
girok addtask "Hangout with Jason" --tmr
```

![](images/girok-addtask4.png)

## 6. Calendar Commands

# 📝 Use Cases

# 🤖 Major updates plan

# 🚒 Troubleshooting

# 😭 Uninstall

# 💌 Contributions
