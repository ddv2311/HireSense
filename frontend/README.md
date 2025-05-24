# AI Hiring Assistant - Frontend

A modern React application for the AI Hiring Assistant system with a beautiful, responsive UI built with Tailwind CSS.

## Features

- 📊 **Interactive Dashboard** - Real-time statistics and charts
- 👥 **Candidate Management** - View, search, and manage candidates
- 📄 **Resume Upload** - Drag-and-drop resume parsing
- 💼 **Job Management** - Create and manage job descriptions
- 📅 **Interview Scheduling** - Schedule and manage interviews
- 💬 **Automated Messaging** - Send automated messages to candidates
- 📱 **Responsive Design** - Works on desktop, tablet, and mobile
- 🎨 **Modern UI** - Clean, professional interface with Tailwind CSS

## Getting Started

### Prerequisites

- Node.js 16+ 
- npm or yarn
- Backend API running on port 8000

### Installation

1. Navigate to the frontend directory:
```bash
cd frontend
```

2. Install dependencies:
```bash
npm install
```

3. Start the development server:
```bash
npm start
```

The application will open at `http://localhost:3000`

## Available Scripts

- `npm start` - Start development server
- `npm build` - Build for production
- `npm test` - Run tests
- `npm run eject` - Eject from Create React App

## UI Components

### Pages
- **Dashboard** - Overview with statistics and charts
- **Jobs** - Job listings and management
- **Candidates** - Candidate listings and profiles
- **Upload Resume** - Resume upload and parsing
- **Schedule** - Interview scheduling
- **Messages** - Automated messaging system

### Components
- **Layout** - Main layout with sidebar navigation
- **ErrorBoundary** - Error handling and display

## Styling

The application uses:
- **Tailwind CSS** - Utility-first CSS framework
- **Lucide React** - Beautiful icons
- **Recharts** - Interactive charts
- **React Hot Toast** - Toast notifications

## API Integration

The frontend connects to the backend API at `http://localhost:8000`. Key endpoints:

- `GET /api/dashboard` - Dashboard statistics
- `POST /api/upload-resume` - Upload and parse resumes
- `GET /api/candidates` - Get candidates list
- `POST /api/upload-jd` - Upload job descriptions
- `GET /api/schedule` - Get interview schedules
- `POST /api/send-message` - Send automated messages

## Troubleshooting

### Common Issues

1. **Styling not loading properly**
   - Ensure Tailwind CSS is properly configured
   - Check that `index.css` is imported in `index.js`
   - Verify all custom CSS classes are defined

2. **API connection errors**
   - Ensure backend server is running on port 8000
   - Check browser console for CORS errors
   - Verify proxy configuration in `package.json`

3. **Charts not displaying**
   - Ensure Recharts is properly installed
   - Check for JavaScript errors in console
   - Verify chart data format

4. **Navigation issues**
   - Check React Router configuration
   - Ensure all routes are properly defined
   - Verify component imports

### Development Tips

1. **Hot Reload**: The development server supports hot reload for instant updates
2. **Error Boundary**: The app includes error boundaries to catch and display errors gracefully
3. **Responsive Design**: Test on different screen sizes using browser dev tools
4. **Console Logs**: Check browser console for any errors or warnings

## Browser Support

- Chrome 90+
- Firefox 88+
- Safari 14+
- Edge 90+

## Performance

- Code splitting with React.lazy (can be added)
- Optimized bundle size with tree shaking
- Responsive images and lazy loading
- Efficient re-renders with React hooks

## Contributing

1. Follow the existing code style
2. Use TypeScript for new components (optional)
3. Add proper error handling
4. Test on multiple screen sizes
5. Update documentation as needed 