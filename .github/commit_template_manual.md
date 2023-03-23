# Apply Commit Template Message

Do `git clone` and you will see .gitmessage.txt

그 후,<br>
Do `git config --local commit.template .github/.gitmessage.txt`<br>
to set the commit template.

Now,<br>
Do `git commit` when you commit instead of `git commit -m "message"`<br>

After completing your commit, just close the commit file or<br>

**✋ For Linux bash or VSCode,**

Type `Ctrl + x`<br>
then you'll see save message, and type `y` to save it.

If you type Enter, then commit is complete!

**✋ For git bash**

Just do `:wq`

<br>

Then `git push`
