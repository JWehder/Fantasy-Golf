import React from 'react'
import ReactDOM from 'react-dom/client'
import { App } from './App'
import './index.css'
import store from './store.jsx';
import { Provider, useDispatch } from "react-redux";
import { RouterProvider, createBrowserRouter } from "react-router-dom";
import SignedOutHome from './components/User/components/home/SignedOutHome.jsx'
import { SignedInHome } from './components/User/components/home/SignedInHome.jsx';
import Dashboard from './components/Leagues/components/Dashboard.js';
import LeagueDashboard from './components/Leagues/components/LeagueDashboard.js';
import ErrorPage from './components/Utils/components/ErrorPage.jsx';
import { QueryClient, QueryClientProvider } from '@tanstack/react-query';
import LeagueSettingsPage from './components/Leagues/components/LeagueSettingsPage';
import DraftPage from './components/Drafts/DraftPage';

// import { ApolloServer } from '@apollo/server';
// import { startStandaloneServer } from '@apollo/server/standalone';

// server setup
// const server = new ApolloServer( {
     // typeDefs: definitions of types of data like player
     // resolvers: 
// });

// const { url } = await startStandaloneServer(server, {
//     listen: { port: 4000 }
// })


const router = createBrowserRouter([
  {
    path:"/",
    element:<App children={undefined} />,
    errorElement: <ErrorPage />, 
    children: [
      {
        path: "/",
        element: <SignedOutHome />,
        errorElement: <ErrorPage /> 
      },
      {
        path: "/leagues",
        element: <SignedInHome children={undefined} />,
        children: [
          {
          path: "/leagues",
          element: <Dashboard />,
          },
          {
            path: "/leagues/:leagueId",
            element: <LeagueDashboard />,
          },
          {
            path: "/leagues/:leagueId/settings",
            element: <LeagueSettingsPage />,
          },
          {
            path: "/leagues/:leagueId/drafts/:draftId",
            element: <DraftPage />,
          }
      ]
      },
      {
        path: 'leagues/:leagueId',
        element: <App><SignedInHome><LeagueDashboard/></SignedInHome></App>
      }
    ]
  }
])

console.log('server ready at port', 4000);

const queryClient = new QueryClient();

ReactDOM.createRoot(document.getElementById('root')!).render(
  <React.StrictMode>
    <QueryClientProvider client={queryClient}>
      <Provider store={store}>
        <RouterProvider router={router} />
      </Provider>
    </QueryClientProvider>
  </React.StrictMode>,
)
