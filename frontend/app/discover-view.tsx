"use client";

import { CalendarDays, Check, Heart, IndianRupee, MapPin, Users, X } from "lucide-react";
import { useRef, useState, type PointerEvent } from "react";

export type DiscoverCard = {
  id: string;
  club_id: string;
  club_name: string;
  club_area: string;
  club_skill_level: string;
  club_rating: number;
  club_description: string;
  club_play_style: string;
  club_player_count: number;
  club_image_url: string;
  venue: string;
  venue_area: string;
  scheduled_at: string;
  cost_per_person: string;
  format: string;
};

type Direction = "like" | "pass";

const dateFormatter = new Intl.DateTimeFormat("en-IN", {
  weekday: "short", day: "numeric", month: "short", timeZone: "Asia/Kolkata"
});
const timeFormatter = new Intl.DateTimeFormat("en-IN", {
  hour: "numeric", minute: "2-digit", hour12: true, timeZone: "Asia/Kolkata"
});

export default function DiscoverView({
  cards,
  clubName,
  onSwipe
}: {
  cards: DiscoverCard[];
  clubName?: string;
  onSwipe: (card: DiscoverCard, direction: Direction) => Promise<boolean>;
}) {
  const [skill, setSkill] = useState("all");
  const visibleCards = cards.filter((card) => skill === "all" || card.club_skill_level === skill);
  const card = visibleCards[0];

  if (!clubName) {
    return <p className="rounded-md bg-slate-100 p-3 text-sm text-slate-600">Create a club before discovering opponent games.</p>;
  }

  return (
    <div className="space-y-4">
      <div className="flex items-start justify-between gap-3">
        <div>
          <h2 className="text-xl font-bold text-slate-950">Discover games</h2>
          <p className="mt-1 text-sm text-slate-500">Playing as {clubName}</p>
        </div>
        <span className="shrink-0 rounded-md bg-emerald-50 px-2 py-1 text-xs font-semibold text-emerald-800">
          {visibleCards.length} available
        </span>
      </div>

      <label className="flex items-center justify-between gap-3 text-sm font-medium text-slate-600">
        Skill level
        <select
          aria-label="Filter by skill level"
          value={skill}
          onChange={(event) => setSkill(event.target.value)}
          className="min-w-32 rounded-md border border-slate-300 bg-white px-2 py-2 text-sm text-slate-900"
        >
          <option value="all">All levels</option>
          <option value="beginner">Beginner</option>
          <option value="casual">Casual</option>
          <option value="intermediate">Intermediate</option>
          <option value="advanced">Advanced</option>
        </select>
      </label>

      {card ? (
        <SwipeCard key={card.id} card={card} onSwipe={onSwipe} />
      ) : (
        <div className="flex min-h-56 flex-col items-center justify-center rounded-md border border-slate-200 bg-white px-5 text-center">
          <Check size={28} className="text-emerald-600" />
          <h3 className="mt-3 font-semibold text-slate-900">You are all caught up</h3>
          <p className="mt-1 text-sm text-slate-500">
            {cards.length ? "No games match this skill level." : "New opponent games will appear here when clubs publish them."}
          </p>
          {cards.length > 0 && <button className="mt-3 text-sm font-semibold text-emerald-700" onClick={() => setSkill("all")}>Show all levels</button>}
        </div>
      )}
    </div>
  );
}

function SwipeCard({
  card,
  onSwipe
}: {
  card: DiscoverCard;
  onSwipe: (card: DiscoverCard, direction: Direction) => Promise<boolean>;
}) {
  const [dragX, setDragX] = useState(0);
  const [busy, setBusy] = useState(false);
  const start = useRef<{ x: number; y: number } | null>(null);

  async function act(direction: Direction) {
    if (busy) return;
    setBusy(true);
    setDragX(direction === "like" ? 520 : -520);
    const succeeded = await onSwipe(card, direction);
    if (!succeeded) {
      setDragX(0);
      setBusy(false);
    }
  }

  function onPointerDown(event: PointerEvent<HTMLElement>) {
    if (busy || !event.isPrimary) return;
    start.current = { x: event.clientX, y: event.clientY };
    event.currentTarget.setPointerCapture(event.pointerId);
  }

  function onPointerMove(event: PointerEvent<HTMLElement>) {
    if (!start.current || busy) return;
    const deltaX = event.clientX - start.current.x;
    const deltaY = event.clientY - start.current.y;
    if (Math.abs(deltaX) > Math.abs(deltaY)) setDragX(deltaX);
  }

  function onPointerUp(event: PointerEvent<HTMLElement>) {
    if (!start.current || busy) return;
    const deltaX = event.clientX - start.current.x;
    start.current = null;
    if (Math.abs(deltaX) > 90) void act(deltaX > 0 ? "like" : "pass");
    else setDragX(0);
  }

  const scheduled = new Date(card.scheduled_at);
  return (
    <div>
      <article
        aria-label={`${card.club_name} game card`}
        onPointerDown={onPointerDown}
        onPointerMove={onPointerMove}
        onPointerUp={onPointerUp}
        onPointerCancel={() => { start.current = null; setDragX(0); }}
        className="overflow-hidden rounded-md border border-slate-200 bg-white shadow-sm select-none"
        style={{
          touchAction: "pan-y",
          transform: `translateX(${dragX}px) rotate(${Math.max(-8, Math.min(8, dragX / 25))}deg)`,
          transition: start.current && !busy ? "none" : "transform 180ms ease-out"
        }}
      >
        <div className="relative h-52 w-full overflow-hidden bg-slate-200">
          {card.club_image_url ? (
            <img src={card.club_image_url} alt={`${card.club_name} football`} className="h-full w-full object-cover" draggable={false} />
          ) : (
            <div className="flex h-full items-center justify-center bg-emerald-800 text-4xl font-bold text-white">{card.club_name.slice(0, 2).toUpperCase()}</div>
          )}
          <span className="absolute right-3 top-3 rounded bg-white px-2 py-1 text-xs font-bold text-slate-900">8v8</span>
        </div>
        <div className="space-y-4 p-4">
          <div>
            <h3 className="text-xl font-bold text-slate-950">{card.club_name}</h3>
            <p className="mt-1 text-sm text-slate-600">{card.club_area} · {card.club_skill_level} · {card.club_player_count} players</p>
          </div>

          <div className="grid grid-cols-2 gap-3 border-y border-slate-100 py-3 text-sm">
            <div className="flex items-start gap-2"><CalendarDays size={17} className="mt-0.5 shrink-0 text-emerald-700" /><span><strong className="block text-slate-900">{dateFormatter.format(scheduled)}</strong>{timeFormatter.format(scheduled)}</span></div>
            <div className="flex items-start gap-2"><MapPin size={17} className="mt-0.5 shrink-0 text-emerald-700" /><span><strong className="block text-slate-900">{card.venue_area}</strong>{card.venue}</span></div>
            <div className="flex items-start gap-2"><IndianRupee size={17} className="mt-0.5 shrink-0 text-emerald-700" /><span><strong className="block text-slate-900">₹{Number(card.cost_per_person).toFixed(0)}</strong>per player</span></div>
            <div className="flex items-start gap-2"><Users size={17} className="mt-0.5 shrink-0 text-emerald-700" /><span><strong className="block text-slate-900">8 ready</strong>opponent needed</span></div>
          </div>

          <p className="text-sm leading-5 text-slate-600">{card.club_description}</p>
          <p className="text-xs text-slate-500">{card.club_play_style}</p>
        </div>
      </article>

      <div className="mt-4 flex gap-3">
        <button
          type="button"
          disabled={busy}
          onClick={() => void act("pass")}
          title="Pass on this game"
          className="flex min-h-12 flex-1 items-center justify-center gap-2 rounded-md border border-slate-300 bg-white text-sm font-semibold text-slate-700 disabled:opacity-50"
        ><X size={19} /> Pass</button>
        <button
          type="button"
          disabled={busy}
          onClick={() => void act("like")}
          title="Request to play this game"
          className="flex min-h-12 flex-1 items-center justify-center gap-2 rounded-md bg-emerald-700 text-sm font-semibold text-white disabled:opacity-50"
        ><Heart size={19} /> Request game</button>
      </div>
      <p className="mt-3 text-center text-xs text-slate-500">The host captain confirms your request.</p>
    </div>
  );
}
