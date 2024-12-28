import React from 'react';
import { render, screen, fireEvent } from '@testing-library/react';
import TournamentScheduleTable from '../TournamentScheduleTable';
import '@testing-library/jest-dom';
import { Tournament } from '../../../../types/tournaments';

// Mock dependencies
jest.mock('./useSettings', () => ({
    useSettings: () => ({
        settings: true,
        disabled: false,
        handleCheckboxChange: jest.fn(),
        selectedTournaments: new Set<string>(),
    }),
}));

jest.mock('./TableHeaders', () => ({ headers }: { headers: string[] }) => (
    <div data-testid="table-headers">{headers.join(', ')}</div>
));

jest.mock('./TableRow', () => ({ firstTwoDatapoints, data, columns, onClick }: any) => (
    <div
        data-testid="table-row"
        onClick={() => onClick(data)}
    >
        {firstTwoDatapoints.map((dp: string, idx: number) => (
            <div key={idx}>{typeof dp === 'string' ? dp : 'Custom Content'}</div>
        ))}
    </div>
));

const mockSetSelectedTournament = jest.fn();

const tournaments: Tournament[] = [
    {
        id: '1',
        StartDate: '2024-01-01',
        EndDate: '2024-01-10',
        Name: 'Tournament A',
        Venue: ['Venue A'],
        City: 'City A',
        State: 'State A',
        Links: ['http://linkA.com'],
        Purse: 1000000,
        PreviousWinner: 'Player A',
        Par: '72',
        Yardage: '7000',
        IsCompleted: false,
        InProgress: true,
        ProSeasonId: 'PS1',
        created_at: '2024-01-01T00:00:00Z',
        updated_at: '2024-01-01T00:00:00Z',
        PreviousWinnerScore: 68,
        Holes: [],
    },
    {
        id: '2',
        StartDate: '2024-02-01',
        EndDate: '2024-02-10',
        Name: 'Tournament B',
        Venue: ['Venue B'],
        City: 'City B',
        State: 'State B',
        Links: ['http://linkB.com'],
        Purse: 2000000,
        PreviousWinner: 'Player B',
        Par: '70',
        Yardage: '7200',
        IsCompleted: true,
        InProgress: false,
        ProSeasonId: 'PS2',
        created_at: '2024-02-01T00:00:00Z',
        updated_at: '2024-02-01T00:00:00Z',
        PreviousWinnerScore: 66,
        Holes: [],
    },
];

describe('TournamentScheduleTable', () => {
    beforeEach(() => {
        jest.clearAllMocks();
    });

    test('renders table headers', () => {
        render(
            <TournamentScheduleTable
                setSelectedTournament={mockSetSelectedTournament}
                tournaments={tournaments}
            />
        );

        const headers = screen.getByTestId('table-headers');
        expect(headers).toHaveTextContent('Date, Tournament Name, Purse, Winner');
    });

    test('renders a row for each tournament', () => {
        render(
            <TournamentScheduleTable
                setSelectedTournament={mockSetSelectedTournament}
                tournaments={tournaments}
            />
        );

        const rows = screen.getAllByTestId('table-row');
        expect(rows).toHaveLength(2); // One for each tournament
    });

    test('displays tournament details correctly', () => {
        render(
            <TournamentScheduleTable
                setSelectedTournament={mockSetSelectedTournament}
                tournaments={tournaments}
            />
        );

        expect(screen.getByText('Tournament A')).toBeInTheDocument();
        expect(screen.getByText('City A, State A')).toBeInTheDocument();
        expect(screen.getByText('Player A')).toBeInTheDocument();
    });

    test('checkboxes are rendered when settings are enabled', () => {
        render(
            <TournamentScheduleTable
                setSelectedTournament={mockSetSelectedTournament}
                tournaments={tournaments}
            />
        );

        const checkboxes = screen.getAllByRole('checkbox');
        expect(checkboxes).toHaveLength(2); // One for each tournament
    });

    test('calls handleCheckboxChange when checkbox is clicked', () => {
        const mockHandleCheckboxChange = jest.fn();
        jest.mock('./useSettings', () => ({
            useSettings: () => ({
                settings: true,
                disabled: false,
                handleCheckboxChange: mockHandleCheckboxChange,
                selectedTournaments: new Set<string>(),
            }),
        }));

        render(
            <TournamentScheduleTable
                setSelectedTournament={mockSetSelectedTournament}
                tournaments={tournaments}
            />
        );

        const checkboxes = screen.getAllByRole('checkbox');
        fireEvent.click(checkboxes[0]);
        expect(mockHandleCheckboxChange).toHaveBeenCalledWith(tournaments[0].id);
    });

    test('calls setSelectedTournament when a row is clicked', () => {
        render(
            <TournamentScheduleTable
                setSelectedTournament={mockSetSelectedTournament}
                tournaments={tournaments}
            />
        );

        const rows = screen.getAllByTestId('table-row');
        fireEvent.click(rows[0]);
        expect(mockSetSelectedTournament).toHaveBeenCalledWith(tournaments[0]);
    });

    test('handles the PreviousWinner to Winner conversion', () => {
        render(
            <TournamentScheduleTable
                setSelectedTournament={mockSetSelectedTournament}
                tournaments={tournaments}
            />
        );

        expect(screen.getByText('Player A')).toBeInTheDocument(); // Winner
    });

    test('renders no checkboxes when settings are disabled', () => {
        jest.mock('./useSettings', () => ({
            useSettings: () => ({
                settings: false,
                disabled: false,
                handleCheckboxChange: jest.fn(),
                selectedTournaments: new Set<string>(),
            }),
        }));

        render(
            <TournamentScheduleTable
                setSelectedTournament={mockSetSelectedTournament}
                tournaments={tournaments}
            />
        );

        const checkboxes = screen.queryAllByRole('checkbox');
        expect(checkboxes).toHaveLength(0);
    });

    test('handles empty tournaments array', () => {
        render(
            <TournamentScheduleTable
                setSelectedTournament={mockSetSelectedTournament}
                tournaments={[]}
            />
        );

        const rows = screen.queryAllByTestId('table-row');
        expect(rows).toHaveLength(0);
    });
});
