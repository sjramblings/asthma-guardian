# Asthma Guardian v3 Frontend

React TypeScript frontend application for the Asthma Guardian v3 air quality monitoring system.

## Features

- **Real-time Dashboard**: Display current air quality data with AQI and pollutant levels
- **User Profile Management**: Manage asthma severity, location, and sensitivity settings
- **Personalized Guidance**: AI-powered recommendations based on air quality and user profile
- **Notification Management**: View notification history and manage preferences
- **Responsive Design**: Works on desktop and mobile devices

## Technology Stack

- React 18 with TypeScript
- Material-UI (MUI) for components
- React Router for navigation
- Axios for API communication
- Emotion for styling

## Getting Started

### Prerequisites

- Node.js 16+ 
- npm or yarn

### Installation

1. Install dependencies:
```bash
npm install
```

2. Create environment file:
```bash
cp .env.example .env
```

3. Update the API URL in `.env` if needed:
```
REACT_APP_API_URL=https://api-dev.asthmaguardian.nsw.gov.au
```

### Development

Start the development server:
```bash
npm start
```

The app will open at http://localhost:3000

### Building for Production

Build the app for production:
```bash
npm run build
```

The build files will be in the `build` directory.

## Project Structure

```
src/
├── api/
│   └── client.ts          # API client for backend communication
├── components/
│   ├── Dashboard.tsx      # Main dashboard component
│   ├── Login.tsx          # Login/authentication component
│   ├── Navbar.tsx         # Navigation bar component
│   ├── Notifications.tsx  # Notification management component
│   └── UserProfile.tsx    # User profile management component
├── App.tsx                # Main app component with routing
├── index.tsx              # App entry point
└── index.css              # Global styles
```

## API Integration

The frontend integrates with the following backend APIs:

- **Air Quality API**: Current, forecast, and historical air quality data
- **User Profile API**: User profile management and preferences
- **Guidance API**: Personalized recommendations using AWS Bedrock
- **Notification API**: Notification management and preferences

## Authentication

Currently uses a demo authentication system. In production, this would integrate with a proper authentication service.

## Environment Variables

- `REACT_APP_API_URL`: Backend API URL (default: https://api-dev.asthmaguardian.nsw.gov.au)

## Available Scripts

- `npm start`: Start development server
- `npm run build`: Build for production
- `npm test`: Run tests
- `npm run eject`: Eject from Create React App (not recommended)