# QR Reader Dashboard - Frontend

A modern React dashboard for the QR Code Reader Premium Platform with analytics visualization and QR management.

## Features

- **Modern React Dashboard** - Clean, responsive interface built with React 18
- **Authentication** - JWT-based login/register with protected routes
- **Analytics Visualization** - Interactive charts and graphs using Recharts
- **QR Code Designer** - Advanced QR code creation with logos, colors, and styling
- **QR Management** - Comprehensive QR code management and organization
- **Settings** - User profile, security, subscription, and privacy settings
- **Real-time Updates** - Live data updates and notifications
- **Responsive Design** - Works on desktop, tablet, and mobile devices

## Tech Stack

- **React 18** - Modern React with hooks and context
- **React Router** - Client-side routing
- **Tailwind CSS** - Utility-first CSS framework
- **Recharts** - Chart library for analytics
- **Axios** - HTTP client for API communication
- **React Hot Toast** - Toast notifications
- **Lucide React** - Beautiful icons
- **React Dropzone** - File upload handling

## Getting Started

### Prerequisites

- Node.js 16+ and npm
- FastAPI backend running on `http://localhost:8000`

### Installation

1. **Install dependencies**
   ```bash
   cd frontend
   npm install
   ```

2. **Start development server**
   ```bash
   npm start
   ```

3. **Open browser**
   Navigate to `http://localhost:3000`

### Environment Variables

Create a `.env` file in the frontend directory:

```env
REACT_APP_API_URL=http://localhost:8000/api/v1
```

## Project Structure

```
frontend/
├── public/
│   └── index.html
├── src/
│   ├── components/
│   │   ├── Layout.js
│   │   └── ProtectedRoute.js
│   ├── contexts/
│   │   ├── AuthContext.js
│   │   └── QRContext.js
│   ├── pages/
│   │   ├── Dashboard.js
│   │   ├── Login.js
│   │   ├── Register.js
│   │   ├── QRDesigner.js
│   │   ├── Analytics.js
│   │   ├── QRManagement.js
│   │   └── Settings.js
│   ├── services/
│   │   └── api.js
│   ├── App.js
│   ├── index.js
│   └── index.css
├── package.json
├── tailwind.config.js
└── postcss.config.js
```

## Features Overview

### Dashboard
- Overview statistics and metrics
- Interactive charts showing scan trends
- Device and browser distribution
- Top performing QR codes
- Real-time data updates

### QR Designer
- Advanced QR code creation
- Multiple templates and styles
- Logo and background integration
- Color customization
- Module style options (square, rounded, circle, gapped)
- Gradient effects
- Custom styling options

### Analytics
- Detailed performance metrics
- Interactive charts and graphs
- Device and browser analytics
- Geographic distribution
- Time-based filtering
- Export capabilities

### QR Management
- Comprehensive QR code listing
- Search and filtering
- Bulk operations
- QR code preview
- Statistics and metrics
- Edit and delete functionality

### Settings
- User profile management
- Password change
- Subscription management
- Notification preferences
- Privacy settings
- Data export

## API Integration

The frontend communicates with the FastAPI backend through:

- **Authentication API** - Login, register, token refresh
- **QR Code API** - Generation, management, analytics
- **QR Designer API** - Advanced styling and templates
- **Analytics API** - Statistics and reporting
- **Subscriptions API** - Plan management and billing
- **Rate Limits API** - Usage monitoring

## Styling

The application uses Tailwind CSS for styling with:

- Custom color palette
- Responsive design system
- Component-based styling
- Dark mode support (planned)
- Accessibility features

## Development

### Available Scripts

- `npm start` - Start development server
- `npm build` - Build for production
- `npm test` - Run tests
- `npm eject` - Eject from Create React App

### Code Style

- ESLint configuration for code quality
- Prettier for code formatting
- Component-based architecture
- Custom hooks for reusable logic
- Context API for state management

## Deployment

### Production Build

```bash
npm run build
```

This creates a `build` folder with optimized production files.

### Environment Configuration

For production deployment, update the API URL:

```env
REACT_APP_API_URL=https://your-api-domain.com/api/v1
```

## Contributing

1. Follow the existing code style
2. Use meaningful component and variable names
3. Add proper error handling
4. Include loading states
5. Test on multiple devices and browsers

## License

MIT License - see LICENSE file for details.
