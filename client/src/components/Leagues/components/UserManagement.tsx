import React, { useEffect, useState } from 'react';
import axios from 'axios';
import { UsersData } from '../../../types/users';
import { useSelector } from 'react-redux';
import { RootState } from '../../../store';
import UsersTable from './UsersTable';
import THead from '../../Utils/components/THead';

interface User {
  id: string;
  Username: string;
  Email: string;
  Team: any;  // Can be further typed based on your Team data
}

const UserManagement: React.FC<{ leagueId: string; isCommish: boolean }> = ({ leagueId, isCommish }) => {
  const [users, setUsers] = useState<User[]>([]);
  const [errors, setErrors] = useState<string | null>(null);

  const leaguesTeams = useSelector((state: RootState) => state.teams.leaguesTeams);
  const numOfTeams = useSelector((state: RootState) => state.leagues.selectedLeague?.LeagueSettings.NumberOfTeams);

  useEffect(() => {
    const fetchUsers = async () => {
      if (!leaguesTeams) return; // Ensure leaguesTeams is loaded before fetching users

      try {
        const response = await axios.get(`/api/leagues/${leagueId}/users`);
        const data = response.data;
        const users = data.map((user: User) => {
          // Find team for the user
          const team = leaguesTeams.find((team) => team.OwnerId === user.id);
          return { ...user, TeamName: team ? team.TeamName : 'No Team' }; // Adding TeamName property to the user object
        });
        setUsers(users);
      } catch (error) {
        console.error('Error fetching league users:', error);
        setErrors('Failed to fetch users.');
      }
    };

    fetchUsers();
  }, [leagueId, leaguesTeams]);

  const columns = new Set(['TeamName', 'Username', 'Email']); // Define columns to show

  return (
    <div className="">
      <h2 className="text-lg font-bold">Manage Users</h2>

        {errors && <div className="text-red-500">{errors}</div>}
        <div className="w-full flex bg-middle text-xs truncate font-bold p-2 items-center text-clip border-b border-light">
            <THead datapoint={"Team Name"} />
            <THead datapoint={"Username"} />
            <THead datapoint={"Email"} />
        </div>
        {users.map((user, idx) => (
            <UsersTable
            key={user.id}
            data={user} // Pass user data to UsersTable
            columns={columns} // Pass the columns to render
            onClick={() => {}} // Handle row click if needed
            brightness={idx % 2 === 0 ? 'brightness-125' : ''}
            disabled={false} // Set to true if you want to disable the row
            />
        ))}
    </div>
  );
};

export default UserManagement;

