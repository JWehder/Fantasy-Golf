import React from 'react';
import { Event } from '../../../types/events';
import { FaCalendarAlt, FaMapMarkerAlt, FaFlagCheckered } from 'react-icons/fa';
import { format, parseISO } from 'date-fns';


type EventItemProps = {
    event: Event;
};

interface ScheduleProps {
  data: {
    pages: {
      events: Event[];
    }[];
  } | undefined;
  fetchNextPage: () => void;
  hasNextPage: boolean | undefined;
  isFetchingNextPage: boolean;
  isError: boolean;
  error: {
    message: string;
  } | null;
}

const formatDate = (date: string) => format(parseISO(date), 'MMMM d, yyyy');

const formatDateRange = (startDate: string, endDate: string) => {
  const start = parseISO(startDate);
  const end = parseISO(endDate);

  // If the month is the same, only show the day difference
  if (start.getMonth() === end.getMonth()) {
    return `${format(start, 'MMMM d')}–${format(end, 'd, yyyy')}`;
  }

  return `${format(start, 'MMMM d, yyyy')} – ${format(end, 'MMMM d, yyyy')}`;
};

const EventItem: React.FC<EventItemProps> = ({ event }) => (
    <div className="p-6 rounded-lg shadow-lg bg-gradient-to-br from-middle to-dark mb-6 transform hover:scale-105 transition-transform duration-200">
        {/* Tournament Name and Dates in the same line */}
        <div className="flex justify-between items-center mb-3">
            <h3 className="text-xl font-bold flex items-center gap-2">
                <FaFlagCheckered /> {event.TournamentName}
            </h3>
            <p className="text-sm flex items-center gap-2 text-light">
                <FaCalendarAlt /> {formatDateRange(event.TournamentStartDate, event.TournamentEndDate)}
            </p>
        </div>

        {/* Venue */}
        <p className="mb-2 flex items-center gap-2">
            <FaMapMarkerAlt />
            <strong>Venue:</strong> {event.TournamentVenue}
        </p>

        {/* Location */}
        <p className="mb-2">
            <strong>Location:</strong> {event.TournamentLocation}
        </p>

        {/* Additional Details */}
        <div className="mt-4 border-t border-white/40 pt-3">
            <p>
                <strong>Draft Start:</strong> {formatDate(event.DraftStartDate)}
            </p>
            <p>
                <strong>Draft Rounds:</strong> {event.DraftRounds}
            </p>
        </div>
    </div>
);



const Schedule: React.FC<ScheduleProps> = ({
    data,
    fetchNextPage,
    hasNextPage,
    isFetchingNextPage,
    isError,
    error
}) => {  
  
    return (
      <div className="w-full py-4 px-24 bg-dark text-light font-PTSans">
        <h1 className="text-4xl font-extrabold text-center text-primary mb-10">
          Upcoming Events
        </h1>
        <div className="flex flex-col gap-12">
          {data?.pages.map((page, pageIndex) => (
            <div key={pageIndex}>
              {page.events.map((event: Event, idx: number) => (
                <EventItem key={idx} event={event} />
              ))}
            </div>
          ))}
        </div>
  
        {hasNextPage && (
          <div className="text-center mt-8">
            <button
              onClick={() => fetchNextPage()}
              disabled={isFetchingNextPage}
              className="inline-block px-8 py-4 bg-primary text-white font-semibold rounded-lg shadow hover:bg-primary-dark transition-all"
            >
              {isFetchingNextPage ? 'Loading...' : 'Load More Events'}
            </button>
          </div>
        )}
  
        {isError && (
          <div className="text-center mt-8">
            <p className="text-red-500 text-lg">
              {error?.message || 'Failed to load events. Please try again later.'}
            </p>
          </div>
        )}
      </div>
    );
  };


export default Schedule;