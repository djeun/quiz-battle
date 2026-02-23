---
name: deploy
description: Push to GitHub and trigger Render.com deployment. Run with /deploy.
user-invocable: true
allowed-tools: Bash
argument-hint: "commit message"
---

Commit all changes and push to GitHub. Render auto-deploys on push.

```bash
cd C:\Users\Administrator\quiz-battle
git add .
git commit -m "$ARGUMENTS"
git push origin main
```

After pushing:
1. Go to your Render dashboard to monitor the deployment
2. Wait ~1-2 min for build to complete
3. Open the Render URL to verify the live deployment works

If no commit message provided, use: `git commit -m "Update"`
