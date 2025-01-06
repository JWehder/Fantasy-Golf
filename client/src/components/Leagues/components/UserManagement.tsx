import React, { useEffect, useState } from 'react';
import axios from 'axios';
import { UsersData } from '../../../types/users';

const UserManagement: React.FC<{ leagueId: string; isCommish: boolean }> = ({ leagueId, isCommish }) => {
  const [users, setUsers] = useState<UsersData[]>([]);
  const [allUsers, setAllUsers] = useState<UsersData[]>([]);
  const [selectedUser, setSelectedUser] = useState<string | null>(null);
  const [errors, setErrors] = useState<string | null>(null);

  useEffect(() => {
    const fetchUsers = async () => {
      try {
        const response = await axios.get(`/api/leagues/${leagueId}/users`);
        setUsers(response.data);
      } catch (error) {
        console.error("Error fetching league users:", error);
      }
    };

    const fetchAllUsers = async () => {
      try {
        const response = await axios.get(`/api/users`);
        setAllUsers(response.data);
      } catch (error) {
        console.error("Error fetching all users:", error);
      }
    };

    fetchUsers();
    fetchAllUsers();
  }, [leagueId]);

  const handleAddUser = async () => {
    if (!selectedUser) {
      setErrors("Please select a user to add.");
      return;
    }

    try {
      await axios.post(`/api/leagues/${leagueId}/users`, { userId: selectedUser });
      setUsers((prev) => [...prev, allUsers.find((user) => user.id === selectedUser)!]);
      setSelectedUser(null);
    } catch (error) {
      console.error("Error adding user to league:", error);
      setErrors("Failed to add user. Please try again.");
    }
  };

  const handleRemoveUser = async (userId: string) => {
    try {
      await axios.delete(`/api/leagues/${leagueId}/users/${userId}`);
      setUsers((prev) => prev.filter((user) => user.id !== userId));
    } catch (error) {
      console.error("Error removing user from league:", error);
    }
  };

  return (
    <div className="space-y-6">
      <h2 className="text-lg font-bold">Manage Users</h2>

      {errors && <div className="text-red-500">{errors}</div>}

      {isCommish && (
        <div className="flex space-x-4">
          <select
            value={selectedUser || ""}
            onChange={(e) => setSelectedUser(e.target.value)}
            className="p-2 rounded bg-light text-dark"
          >
            <option value="">Select a user</option>
            {allUsers
              .filter((user) => !users.find((u) => u.id === user.id))
              .map((user) => (
                <option key={user.id} value={user.id}>
                  {user.name}
                </option>
              ))}
          </select>
          <button onClick={handleAddUser} className="px-4 py-2 bg-highlightBlue text-light rounded">
            Add User
          </button>
        </div>
      )}

      <table className="w-full bg-light text-dark rounded-lg">
        <thead>
          <tr>
            <th className="px-4 py-2">User Name</th>
            <th className="px-4 py-2">Email</th>
            <th className="px-4 py-2">Actions</th>
          </tr>
        </thead>
        <tbody>
          {users.map((user, idx) => (
            <tr key={`user-${idx}`}>
              <td className="px-4 py-2">username</td>
              <td className="px-4 py-2">email</td>
              <td className="px-4 py-2">
                {isCommish && (
                  <button
                    onClick={() => handleRemoveUser(user.id)}
                    className="px-2 py-1 bg-red-500 text-light rounded"
                  >
                    Remove
                  </button>
                )}
              </td>
            </tr>
          ))}
        </tbody>
      </table>
    </div>
  );
};
