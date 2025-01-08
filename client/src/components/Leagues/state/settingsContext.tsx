import React, { createContext, useContext, useState } from 'react';

interface SettingsContextProps {
  selectedTournaments: Set<string>;
  setSelectedTournaments: React.Dispatch<React.SetStateAction<Set<string>>>;
  handleCheckboxChange: (tournamentId: string) => void;
  settings: boolean;
  disabled: boolean;

}

// Default context values
const defaultSettings: SettingsContextProps = {
    settings: false,
    disabled: false,
    handleCheckboxChange: () => {},
    selectedTournaments: new Set(),
    setSelectedTournaments: () => {}
};

const SettingsContext = createContext<SettingsContextProps | undefined>(undefined);

export const SettingsProvider: React.FC<{ children: React.ReactNode }> = ({ children }) => {
  const [selectedTournaments, setSelectedTournaments] = useState<Set<string>>(new Set());

  const handleCheckboxChange = (tournamentId: string) => {
    setSelectedTournaments((prev) =>
      prev.has(tournamentId)
        ? new Set([...prev].filter((id) => id !== tournamentId))
        : new Set([...prev, tournamentId])
    );
  };

  const settings = true;
  const disabled = true;

  return (
    <SettingsContext.Provider
      value={{ settings, disabled, handleCheckboxChange, selectedTournaments, setSelectedTournaments }}
    >
      {children}
    </SettingsContext.Provider>
  );
};

export const useSettings = () => {
  const context = useContext(SettingsContext);
  return context || defaultSettings;
};
