# Deployment Guide

## Deploy to Render.com (Free)

### Prerequisites
- GitHub account with this repository
- Render.com account (free at https://render.com)

### Steps

1. **Sign up / Log in to Render.com**
   - Go to https://render.com
   - Sign up or log in with your GitHub account

2. **Connect Your GitHub Repository**
   - Click "New +" button in the dashboard
   - Select "Blueprint"
   - Connect your GitHub account if not already connected
   - Select this repository: `chulpaeve-max/kanban-project-management-mvp`

3. **Configure Environment Variables**
   - Render will detect the `render.yaml` file automatically
   - You'll be prompted to add environment variables
   - Add your `OPENROUTER_API_KEY` value

4. **Deploy**
   - Click "Apply" to start the deployment
   - Render will build the Docker container and deploy
   - First deployment takes 5-10 minutes

5. **Access Your App**
   - Once deployed, you'll get a URL like: `https://kanban-studio.onrender.com`
   - The app will be live at this URL

### Important Notes

**Database:**
- Current setup uses SQLite which is stored in the container
- Data will be lost on redeployments
- For production, consider upgrading to Render's PostgreSQL (free tier available)

**Free Tier Limitations:**
- App goes to sleep after 15 minutes of inactivity
- First request after sleep takes ~30 seconds to wake up
- 750 hours/month of runtime (enough for personal use)

**Custom Domain:**
- Can add custom domain in Render dashboard (Settings > Custom Domain)

### Alternative: Deploy to Railway.app

1. Go to https://railway.app
2. Sign in with GitHub
3. Click "New Project" > "Deploy from GitHub repo"
4. Select this repository
5. Add environment variable: `OPENROUTER_API_KEY`
6. Railway will auto-detect Docker and deploy
7. Get your URL from the deployment settings

### Alternative: Deploy to Fly.io

1. Install flyctl: https://fly.io/docs/hands-on/install-flyctl/
2. Run in terminal:
   ```bash
   fly auth login
   fly launch
   fly secrets set OPENROUTER_API_KEY=your_key_here
   fly deploy
   ```

## Monitoring

After deployment:
- Check logs in Render dashboard > Logs tab
- Monitor health at: https://your-app.onrender.com/api/health
- Test login with: username=user, password=password
