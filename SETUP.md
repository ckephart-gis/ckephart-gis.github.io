# Getting this site live — step by step

## 1. Create your GitHub account
Go to https://github.com and sign up (free). Pick a username you're fine
with recruiters seeing, since it becomes part of your site's URL.

## 2. Create the right repository
- Click the **+** icon (top right) → **New repository**
- Name it **exactly**: `yourusername.github.io` (swap in your real username)
- Set visibility to **Public**
- Click **Create repository** (don't add a README, you already have one)

The exact name `yourusername.github.io` is what tells GitHub to serve it
as a live website automatically, at that same URL.

## 3. Upload these files
On your new (empty) repo page:
- Click **Add file → Upload files**
- Unzip the folder I gave you, then drag in *everything* — including the
  `css`, `js`, `projects`, and `assets` folders and all files inside them
- Scroll down, click **Commit changes**

No command line needed for this. GitHub's web uploader preserves the
folder structure as long as you drag in the folders themselves.

## 4. Turn on GitHub Pages
- In your repo, go to **Settings → Pages**
- Under **Source**, choose **Deploy from a branch**
- Branch: **main**, folder: **/ (root)** → **Save**
- Wait 1-2 minutes, then visit `https://yourusername.github.io`

## 5. Add your resume
Drop a PDF named exactly `resume.pdf` into the `assets` folder (upload it
the same way, via Add file → Upload files, into that folder). The
"Download Resume" button on the homepage already points to it.

## 6. Customize
Search the files for `your.email@example.com`, `your-profile`, and
`your-username` and swap in your real contact info (found in
`index.html`, `projects/annotation-cartography.html`, and
`projects/template.html`).

## 7. Add more projects
Duplicate `projects/template.html`, rename it, fill in the TODOs, and add
a matching card to the `projects-grid` section in `index.html` (copy one
of the existing `<a class="sheet">` blocks as a starting point).

## Updating the site later
Any time you want to change something: edit the file locally, then on
GitHub go to that file → the pencil (edit) icon → make your change →
Commit. The live site updates within a minute, no redeploy step needed.
