# Web3 Job Board - React App

A modern, responsive job board for the Web3 ecosystem built with React, Vite, and Tailwind CSS.

## 🚀 Quick Start

### Prerequisites
- Node.js 16+ and npm

### Installation

```bash
# Install dependencies
npm install

# Start development server
npm run dev

# Build for production
npm run build

# Preview production build
npm run preview
```

The app will open at `http://localhost:3000`

## 📦 Features

- ✨ Modern cyber-minimal design
- 🔍 Real-time search and filtering
- 📱 Fully responsive
- 🔐 Social authentication (Google, LinkedIn)
- 💾 Save jobs locally
- ⚡ Fast performance with Vite
- 🎨 Tailwind CSS styling
- 🔥 React 18 with hooks

## 🛠️ Tech Stack

- **React 18** - UI framework
- **Vite** - Build tool and dev server
- **Tailwind CSS** - Styling
- **Lucide React** - Icons
- **LocalStorage** - Client-side data persistence

## 📁 Project Structure

```
src/
├── App.jsx       # Main application component
├── main.jsx      # Entry point
└── index.css     # Global styles with Tailwind

public/           # Static assets
```

## 🎨 Customization

### Colors
Edit the primary colors in `src/App.jsx` or `tailwind.config.js`:

```js
// Cyan accent
from-cyan-400 to-blue-500

// Background
bg-[#0a0a0f]
```

### Sectors
Add or modify job sectors in `src/App.jsx`:

```jsx
const SECTORS = [
  { id: 'all', name: 'All Jobs', icon: Globe },
  // Add your custom sector here
];
```

## 🚢 Deployment

### Vercel
```bash
npm run build
# Deploy dist/ folder to Vercel
```

### Netlify
```bash
npm run build
# Deploy dist/ folder to Netlify
```

### Static Hosting
```bash
npm run build
# Upload dist/ folder to any static host
```

## 🔗 Backend Integration

To connect to the Python backend API:

1. Update API endpoints in `src/App.jsx`
2. Replace `SAMPLE_JOBS` with API calls
3. Set up CORS on your backend

Example:
```jsx
useEffect(() => {
  fetch('http://localhost:5000/api/jobs')
    .then(res => res.json())
    .then(data => setJobs(data.jobs));
}, []);
```

## 📝 License

Open source - use freely for your projects!

## 🤝 Contributing

Pull requests are welcome! For major changes, please open an issue first.
