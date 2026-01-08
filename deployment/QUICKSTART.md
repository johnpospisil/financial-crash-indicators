# Deployment Quickstart

Choose your platform and follow the quick steps to deploy:

## 🐳 Docker (Fastest - 5 minutes)

1. **Set environment variables:**

   ```bash
   echo "FRED_API_KEY=your_key_here" > .env
   ```

2. **Start with docker-compose:**

   ```bash
   docker-compose up -d
   ```

3. **Access:** http://localhost:8050

---

## 🚀 Heroku (10 minutes)

1. **Install Heroku CLI:**

   ```bash
   brew install heroku/brew/heroku
   heroku login
   ```

2. **Create app and deploy:**

   ```bash
   heroku create your-app-name
   heroku config:set FRED_API_KEY=your_key_here
   git push heroku main
   ```

3. **Access:** Your app will open automatically

---

## 🎨 Render (15 minutes)

1. **Push to GitHub:**

   ```bash
   git add .
   git commit -m "Deploy"
   git push origin main
   ```

2. **Deploy on Render:**

   - Go to https://render.com
   - Click "New +" → "Blueprint"
   - Connect your repository
   - Set `FRED_API_KEY` in environment variables

3. **Access:** Your dashboard URL from Render

---

## 🖥️ VPS (30 minutes)

**Requirements:** Ubuntu/Debian server with root access

1. **SSH to server:**

   ```bash
   ssh user@your-server-ip
   ```

2. **Run quick install:**

   ```bash
   # Clone repository
   git clone https://github.com/yourusername/recession-dashboard.git /opt/recession-dashboard
   cd /opt/recession-dashboard

   # Install dependencies
   sudo apt update
   sudo apt install -y python3.12 python3-pip python3-venv nginx certbot

   # Setup application
   python3.12 -m venv venv
   source venv/bin/activate
   pip install -r web_app/requirements.txt

   # Set API key
   echo "FRED_API_KEY=your_key_here" > .env

   # Setup systemd service
   sudo cp deployment/systemd_service.conf /etc/systemd/system/recession-dashboard.service
   sudo nano /etc/systemd/system/recession-dashboard.service  # Update paths and API key
   sudo systemctl enable --now recession-dashboard

   # Setup nginx
   sudo cp deployment/nginx.conf /etc/nginx/sites-available/recession-dashboard
   sudo nano /etc/nginx/sites-available/recession-dashboard  # Update server_name
   sudo ln -s /etc/nginx/sites-available/recession-dashboard /etc/nginx/sites-enabled/
   sudo nginx -t && sudo systemctl reload nginx

   # Get SSL certificate
   sudo certbot --nginx -d your-domain.com
   ```

3. **Access:** https://your-domain.com

---

## 📚 Full Documentation

For detailed instructions, troubleshooting, and advanced configuration:

- See [deployment/DEPLOYMENT_GUIDE.md](deployment/DEPLOYMENT_GUIDE.md)
- Automation setup: [scripts/AUTOMATION_GUIDE.md](scripts/AUTOMATION_GUIDE.md)

## 🔑 Get Your FRED API Key

1. Visit https://fred.stlouisfed.org/
2. Create free account
3. Go to "My Account" → "API Keys"
4. Generate new API key

## ✅ Verify Deployment

Once deployed, verify:

- [ ] Dashboard loads at your URL
- [ ] Charts display economic indicators
- [ ] No errors in browser console (F12)
- [ ] Risk gauge shows current recession probability
- [ ] Date range controls work
- [ ] CSV export downloads data

## 🆘 Troubleshooting

**Dashboard won't start?**

- Check FRED API key is set correctly
- View logs: `docker-compose logs` or `heroku logs --tail`
- Verify Python version: 3.12+

**Charts not loading?**

- Wait 30-60 seconds for initial data fetch
- Check FRED API is accessible: https://fred.stlouisfed.org/
- Clear browser cache

**Need help?**

- Check logs first
- Review full deployment guide
- Verify environment variables are set
