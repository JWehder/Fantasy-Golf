import { useEffect, useState } from 'react';
import { GoogleOAuthProvider } from '@react-oauth/google';
import axios from 'axios';
import Header from './components/Utils/components/Header';
import { useSelector } from 'react-redux';
import { Outlet } from "react-router-dom";
import React from 'react';
import { RootState } from './store';
import { AppDispatch } from './store';
import { useDispatch } from 'react-redux';
import { getUser } from './components/User/state/userSlice';
import LoadingScreen from './components/Utils/components/LoadingScreen';

interface AppProps {
  children: React.ReactNode;
}

export const App: React.FC<AppProps> = ({ children }) => {
  const [clientId, setClientId] = useState();
  const dispatch = useDispatch<AppDispatch>();

  const signedIn = useSelector((state: RootState) => state.users.user);

  useEffect(() => {
    // Make the GET request to retrieve the client ID
    axios.get('/api/get_client_id')
        .then(response => {
            setClientId(response.data.client_id);
        })
        .catch(error => {
            // Handle errors if necessary
            console.error('Error fetching client ID:', error);
        });
  }, [clientId]); 

  useEffect(() => {
    dispatch(getUser());
    console.log(signedIn)
  }, []); 

  if (!clientId) return <LoadingScreen />

  return (
    <div className=' bg-dark w-max relative min-h-[calc(100vh-200px)]'>
      <Header />
      <GoogleOAuthProvider clientId={clientId}>
          <Outlet />
      </GoogleOAuthProvider>
    </div>
  ) 
}
