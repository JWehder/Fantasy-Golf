import React from 'react';
import { render, screen, fireEvent, waitFor } from '@testing-library/react';
import Leaderboard from '../Leaderboard';
import { useSelector } from 'react-redux';
import { useFetchTournamentDetails } from '../../../../hooks/tournaments';
import '@testing-library/jest-dom';
import { Tournament } from '../../../../types/tournaments';

// Mock the hooks and components used in Leaderboard
jest.mock('react-redux', () => ({
    useSelector: jest.fn(),
}));

jest.mock('../../../../hooks/tournaments', () => ({
    useFetchTournamentDetails: jest.fn(),
}));

jest.mock('../../../Utils/components/BackButton', () => ({
    __esModule: true,
    default: ({ handleBackClick }: { handleBackClick: () => void }) => (
        <button onClick={handleBackClick}>Back</button>
    ),
}));

jest.mock('./Tourney', () => ({
    __esModule: true,
    default: ({ tournament }: { tournament: Tournament }) => (
        <div data-testid="tourney">{tournament.Name}</div>
    ),
}));

jest.mock('../../../Golfers/components/GolferTournamentDetailsTable', () => ({
    __esModule: true,
    default: ({ tournamentId, holeData }: { tournamentId: string; holeData: any }) => (
        <div data-testid="golfer-tournament-details">{tournamentId} - {holeData.length} holes</div>
    ),
}));

jest.mock('./TournamentScheduleTable', () => ({
    __esModule: true,
    default: ({ setSelectedTournament, tournaments }: { setSelectedTournament: (t: Tournament) => void, tournaments: Tournament[] }) => (
        <div data-testid="tournament-schedule">
            {tournaments.map(tournament => (
                <div key={tournament.id} onClick={() => setSelectedTournament(tournament)}>
                    {tournament.Name}
                </div>
            ))}
        </div>
    ),
}));

jest.mock('../../../Utils/components/SkeletonTable', () => ({
    __esModule: true,
    default: () => <div data-testid="skeleton-table">Loading...</div>,
}));

// Mock the hooks and components used in Leaderboard
jest.mock('react-redux', () => ({
    useSelector: jest.fn(),
}));

const mockUseFetchTournamentDetails = useFetchTournamentDetails as jest.Mock;

describe('Leaderboard', () => {
    const mockTournaments: Tournament[] = [
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
    ];

    beforeEach(() => {
        jest.clearAllMocks();
    });

    test('renders loading skeleton when fetching tournament details', () => {
        mockUseFetchTournamentDetails.mockReturnValue({
            data: { tournaments: [] },
            isFetching: true,
            isSuccess: false,
            isError: false,
        });

        render(<Leaderboard />);

        expect(screen.getByTestId('skeleton-table')).toBeInTheDocument();
    });

    test('renders error message when fetching fails', () => {
        mockUseFetchTournamentDetails.mockReturnValue({
            data: { tournaments: [] },
            isFetching: false,
            isSuccess: false,
            isError: true,
        });

        render(<Leaderboard />);

        expect(screen.getByText('Error loading tournament details.')).toBeInTheDocument();
    });

    test('renders TournamentScheduleTable when data is successful', async () => {
        mockUseFetchTournamentDetails.mockReturnValue({
            data: { tournaments: mockTournaments },
            isFetching: false,
            isSuccess: true,
            isError: false,
        });

        render(<Leaderboard />);

        expect(screen.getByTestId('tournament-schedule')).toBeInTheDocument();
        expect(screen.getByText('Tournament A')).toBeInTheDocument();
    });

    test('selecting a tournament renders the selected tournament and its details', async () => {
        mockUseFetchTournamentDetails.mockReturnValue({
            data: { tournaments: mockTournaments },
            isFetching: false,
            isSuccess: true,
            isError: false,
        });

        render(<Leaderboard />);

        const tournamentName = screen.getByText('Tournament A');
        fireEvent.click(tournamentName);

        await waitFor(() => expect(screen.getByTestId('tourney')).toHaveTextContent('Tournament A'));
        expect(screen.getByTestId('golfer-tournament-details')).toHaveTextContent('1 - 0 holes');
    });

    test('clicking back button resets the selected tournament', async () => {
        mockUseFetchTournamentDetails.mockReturnValue({
            data: { tournaments: mockTournaments },
            isFetching: false,
            isSuccess: true,
            isError: false,
        });

        render(<Leaderboard />);

        // Simulate selecting a tournament
        const tournamentName = screen.getByText('Tournament A');
        fireEvent.click(tournamentName);

        // Verify that the tournament details are rendered
        expect(screen.getByTestId('tourney')).toHaveTextContent('Tournament A');
        expect(screen.getByTestId('golfer-tournament-details')).toHaveTextContent('1 - 0 holes');

        // Simulate clicking the back button
        const backButton = screen.getByText('Back');
        fireEvent.click(backButton);

        // Verify that the tournament details are reset
        expect(screen.queryByTestId('tourney')).not.toBeInTheDocument();
        expect(screen.queryByTestId('golfer-tournament-details')).not.toBeInTheDocument();
    });

    test('renders empty state if no tournaments are available', () => {
        mockUseFetchTournamentDetails.mockReturnValue({
            data: { tournaments: [] },
            isFetching: false,
            isSuccess: true,
            isError: false,
        });

        render(<Leaderboard />);

        expect(screen.queryByTestId('tournament-schedule')).not.toBeInTheDocument();
    });
});
