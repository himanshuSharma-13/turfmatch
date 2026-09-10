"use client";

import {
  Bell,
  CalendarDays,
  Check,
  ChevronLeft,
  ChevronRight,
  Clock3,
  Filter,
  Heart,
  Home,
  MapPin,
  MessageCircle,
  ShieldCheck,
  SlidersHorizontal,
  Sparkles,
  Star,
  User,
  Users,
  X
} from "lucide-react";
import { useMemo, useState } from "react";

type Skill = "Casual" | "Intermediate";
type Tab = "clubs" | "matches" | "profile";

type Club = {
  id: number;
  name: string;
  area: string;
  distanceKm: number;
  skill: Skill;
  playerCount: number;
  openSlots: number;
  availability: string;
  rating: number;
  style: string;
  captain: string;
  image: string;
  tags: string[];
};

type MatchRequest = {
  id: number;
  title: string;
  meta: string;
  status: "Pending" | "Accepted" | "Needs reply";
  type: "Club match" | "Club invite";
};

const clubs: Club[] = [
  {
    id: 1,
    name: "Data FC",
    area: "Andheri West",
    distanceKm: 3.2,
    skill: "Intermediate",
    playerCount: 10,
    openSlots: 2,
    availability: "Weeknights after 8 PM",
    rating: 4.4,
    style: "Passing-heavy, compact shape, quick counters",
    captain: "Demo Captain",
    image:
      "https://images.unsplash.com/photo-1551958219-acbc608c6377?auto=format&fit=crop&w=900&q=80",
    tags: ["10-man roster", "Club match ready", "Verified"]
  },
  {
    id: 2,
    name: "Juhu Strikers",
    area: "Juhu",
    distanceKm: 4.9,
    skill: "Intermediate",
    playerCount: 8,
    openSlots: 1,
    availability: "Tomorrow, 8:30 PM",
    rating: 4.8,
    style: "High press, direct attacks, strong tackles",
    captain: "Rival Captain",
    image:
      "https://images.unsplash.com/photo-1526232761682-d26e03ac148e?auto=format&fit=crop&w=900&q=80",
    tags: ["8 players", "Strong press", "Match ready"]
  },
  {
    id: 3,
    name: "Bandra United",
    area: "Bandra",
    distanceKm: 6.5,
    skill: "Casual",
    playerCount: 9,
    openSlots: 3,
    availability: "Sun, 7:00 PM",
    rating: 4.6,
    style: "Friendly tempo, organized buildup, balanced play",
    captain: "Rohan",
    image:
      "https://images.unsplash.com/photo-1431324155629-1a6deb1dec8d?auto=format&fit=crop&w=900&q=80",
    tags: ["Friendly club", "Flexible slots", "Regular games"]
  }
];

const requests: MatchRequest[] = [
  {
    id: 1,
    title: "Request sent to Juhu Strikers",
    meta: "Club match request, tomorrow at Juhu Turf Park",
    status: "Pending",
    type: "Club match"
  },
  {
    id: 2,
    title: "Bandra United invited a fixture",
    meta: "Club match offer waiting for your reply",
    status: "Needs reply",
    type: "Club match"
  },
  {
    id: 3,
    title: "Data FC accepted your club challenge",
    meta: "Home ground confirmed for Sunday evening",
    status: "Accepted",
    type: "Club invite"
  }
];

const navItems: Array<{ id: Tab; label: string; icon: typeof Home }> = [
  { id: "clubs", label: "Clubs", icon: Home },
  { id: "matches", label: "Matches", icon: Users },
  { id: "profile", label: "Profile", icon: User }
];

export default function HomePage() {
  const [activeTab, setActiveTab] = useState<Tab>("clubs");
  const [clubIndex, setClubIndex] = useState(0);
  const [skillFilter, setSkillFilter] = useState<Skill | "Any">("Any");
  const [distance, setDistance] = useState(8);

  const filteredClubs = useMemo(
    () =>
      clubs.filter(
        (club) =>
          club.distanceKm <= distance &&
          (skillFilter === "Any" || club.skill === skillFilter)
      ),
    [distance, skillFilter]
  );

  const currentClub = filteredClubs[clubIndex % Math.max(filteredClubs.length, 1)];

  function nextClub() {
    setClubIndex((value) => value + 1);
  }

  return (
    <main className="phone-shell relative flex min-h-screen flex-col overflow-hidden">
      <AppHeader />

      <section className="flex-1 overflow-y-auto px-4 pb-28 pt-3">
        {activeTab === "clubs" && (
          <DiscoveryView
            title="Club match discovery"
            subtitle="Find rival clubs for your captain and arrange a clean club-vs-club fixture."
            skillFilter={skillFilter}
            distance={distance}
            onSkillChange={setSkillFilter}
            onDistanceChange={setDistance}
          >
            {currentClub ? (
              <ClubCard club={currentClub} onPass={nextClub} onRequest={nextClub} />
            ) : (
              <EmptyState text="No clubs match these filters." />
            )}
          </DiscoveryView>
        )}

        {activeTab === "matches" && <RequestsView />}
        {activeTab === "profile" && <ProfileView />}
      </section>

      <BottomNav activeTab={activeTab} onChange={setActiveTab} />
    </main>
  );
}

function AppHeader() {
  return (
    <header className="sticky top-0 z-20 border-b border-[#eef1ee] bg-white/90 px-4 py-3 backdrop-blur-sm">
      <div className="flex items-center justify-between">
        <div>
          <p className="text-[10px] font-bold uppercase tracking-[0.2em] text-[#647067]">
            TurfMatch
          </p>
          <h1 className="mt-1 text-lg font-black text-[#171d1a]">Mumbai</h1>
        </div>
        <div className="flex items-center gap-2">
          <button
            aria-label="Filters"
            className="grid h-9 w-9 place-items-center rounded-full border border-[#e7ebe7] bg-[#f8faf7] text-[#17201b]"
            title="Filters"
          >
            <SlidersHorizontal size={18} />
          </button>
          <button
            aria-label="Notifications"
            className="grid h-9 w-9 place-items-center rounded-full border border-[#e7ebe7] bg-[#f8faf7] text-[#17201b]"
            title="Notifications"
          >
            <Bell size={18} />
          </button>
        </div>
      </div>
    </header>
  );
}

function DiscoveryView({
  title,
  subtitle,
  skillFilter,
  distance,
  onSkillChange,
  onDistanceChange,
  children
}: {
  title: string;
  subtitle: string;
  skillFilter: Skill | "Any";
  distance: number;
  onSkillChange: (value: Skill | "Any") => void;
  onDistanceChange: (value: number) => void;
  children: React.ReactNode;
}) {
  return (
    <div className="space-y-3">
      <div>
        <h2 className="text-[26px] font-black leading-none text-[#171d1a]">{title}</h2>
        <p className="mt-2 text-sm leading-5 text-[#647067]">{subtitle}</p>
      </div>

      <div className="rounded-2xl border border-[#edf1ee] bg-[#f8faf7] p-3">
        <div className="flex items-center justify-between gap-3">
          <div className="flex items-center gap-2 text-xs font-bold uppercase tracking-[0.12em] text-[#647067]">
            <Filter size={12} />
            Filter
          </div>
          <div className="text-xs font-semibold text-[#17201b]">Within {distance} km</div>
        </div>

        <div className="mt-3 flex gap-2 overflow-x-auto pb-1">
          {(["Any", "Casual", "Intermediate"] as const).map((skill) => (
            <button
              key={skill}
              className={`shrink-0 rounded-full border px-3 py-1.5 text-sm font-semibold ${
                skillFilter === skill
                  ? "border-[#171d1a] bg-[#171d1a] text-white"
                  : "border-[#e4e8e4] bg-white text-[#17201b]"
              }`}
              onClick={() => onSkillChange(skill)}
            >
              {skill}
            </button>
          ))}
        </div>

        <input
          className="mt-3 w-full accent-[#171d1a]"
          max="12"
          min="2"
          onChange={(event) => onDistanceChange(Number(event.target.value))}
          type="range"
          value={distance}
        />
      </div>

      {children}
    </div>
  );
}

function ClubCard({
  club,
  onPass,
  onRequest
}: {
  club: Club;
  onPass: () => void;
  onRequest: () => void;
}) {
  return (
    <article className="overflow-hidden rounded-[24px] border border-[#edf1ee] bg-white shadow-[0_10px_30px_rgba(18,27,22,0.04)]">
      <div className="relative h-40 overflow-hidden border-b border-[#eef1ee]">
        <img alt={club.name} className="h-full w-full object-cover" src={club.image} />
        <div className="absolute inset-0 bg-gradient-to-t from-[#0d1713]/70 via-[#0d1713]/10 to-transparent" />
        <div className="absolute left-4 top-4 flex flex-wrap gap-2">
          {club.tags.slice(0, 2).map((tag) => (
            <span
              className="rounded-full border border-white/30 bg-white/10 px-2 py-1 text-[10px] font-bold uppercase tracking-[0.12em] text-white backdrop-blur-sm"
              key={tag}
            >
              {tag}
            </span>
          ))}
        </div>
      </div>

      <div className="p-4">
        <div className="flex items-start justify-between gap-3">
          <div>
            <h3 className="text-[28px] font-black leading-none text-[#171d1a]">{club.name}</h3>
            <div className="mt-2 flex items-center gap-2 text-sm text-[#647067]">
              <MapPin size={14} />
              {club.area} · {club.distanceKm} km
            </div>
          </div>
          <div className="rounded-full border border-[#e8eee8] bg-[#f7faf7] px-2.5 py-1 text-xs font-bold text-[#17201b]">
            {club.skill}
          </div>
        </div>

        <div className="mt-4 grid grid-cols-3 gap-2">
          <MiniStat label="Players" value={`${club.playerCount}`} />
          <MiniStat label="Slots" value={`${club.openSlots}`} />
          <MiniStat label="Rating" value={club.rating.toFixed(1)} />
        </div>

        <div className="mt-4 space-y-2 text-sm text-[#37413d]">
          <div className="flex items-center gap-2">
            <CalendarDays size={14} className="text-[#647067]" />
            <span>{club.availability}</span>
          </div>
          <div className="flex items-center gap-2">
            <ShieldCheck size={14} className="text-[#647067]" />
            <span>{club.captain}</span>
          </div>
        </div>

        <div className="mt-4">
          <ActionButtons onPass={onPass} onRequest={onRequest} requestLabel="Request match" />
        </div>
      </div>
    </article>
  );
}

function ActionButtons({
  onPass,
  onRequest,
  requestLabel
}: {
  onPass: () => void;
  onRequest: () => void;
  requestLabel: string;
}) {
  return (
    <div className="grid grid-cols-[42px_1fr_42px] gap-2.5">
      <button
        aria-label="Pass"
        className="grid aspect-square place-items-center rounded-full border border-[#e7ebe7] bg-[#f9faf9] text-[#17201b]"
        onClick={onPass}
      >
        <X size={18} />
      </button>
      <button
        className="flex min-h-12 items-center justify-center gap-2 rounded-full bg-[#171d1a] px-4 text-sm font-bold text-white"
        onClick={onRequest}
      >
        <Heart size={16} />
        {requestLabel}
      </button>
      <button
        aria-label="Next"
        className="grid aspect-square place-items-center rounded-full border border-[#e7ebe7] bg-[#f9faf9] text-[#17201b]"
        onClick={onPass}
      >
        <ChevronRight size={18} />
      </button>
    </div>
  );
}

function RequestsView() {
  return (
    <div className="space-y-4">
      <div>
        <h2 className="text-2xl font-black">Matches</h2>
        <p className="mt-1 text-sm leading-5 text-[#647067]">
          Track club-vs-club fixtures and match invitations in one place.
        </p>
      </div>

      <div className="grid gap-3">
        {requests.map((request) => (
          <article
            className="rounded-lg border border-[#dfe5dc] bg-white p-4 shadow-sm"
            key={request.id}
          >
            <div className="flex items-start justify-between gap-3">
              <div>
                <p className="text-xs font-bold uppercase tracking-wide text-[#1f7a4d]">
                  {request.type}
                </p>
                <h3 className="mt-1 text-base font-black">{request.title}</h3>
                <p className="mt-1 text-sm leading-5 text-[#647067]">{request.meta}</p>
              </div>
              <StatusBadge status={request.status} />
            </div>
            <div className="mt-4 flex gap-2">
              <button className="flex flex-1 items-center justify-center gap-2 rounded-full bg-[#17201b] px-3 py-3 text-sm font-black text-white">
                <MessageCircle size={17} />
                Open
              </button>
              <button className="grid aspect-square w-11 place-items-center rounded-full border border-[#dfe5dc] bg-white text-[#1f7a4d]">
                <Check size={18} />
              </button>
            </div>
          </article>
        ))}
      </div>
    </div>
  );
}

function ProfileView() {
  return (
    <div className="space-y-4">
      <div className="rounded-lg bg-[#17201b] p-5 text-white">
        <div className="flex items-center gap-4">
          <div className="grid h-16 w-16 place-items-center rounded-full bg-[#c7f464] text-2xl font-black text-[#17201b]">
            SD
          </div>
          <div>
            <p className="text-sm font-bold text-[#c7f464]">Phone verified</p>
            <h2 className="text-2xl font-black">Sharminda</h2>
            <p className="text-sm text-white/75">Club captain</p>
          </div>
        </div>
      </div>

      <ProfilePanel
        title="Club profile"
        rows={[
          ["Club", "Data FC"],
          ["Area", "Andheri West"],
          ["Roster", "10 players total"],
          ["Availability", "Weeknights after 8 PM"]
        ]}
      />
      <ProfilePanel
        title="Match setup"
        rows={[
          ["Preferred format", "Club vs club"],
          ["Skill level", "Intermediate"],
          ["Home turf", "Arena 52"],
          ["Open slots", "2 players available"]
        ]}
      />
    </div>
  );
}

function ProfilePanel({ title, rows }: { title: string; rows: Array<[string, string]> }) {
  return (
    <section className="rounded-lg border border-[#dfe5dc] bg-white p-4">
      <div className="flex items-center justify-between">
        <h3 className="text-lg font-black">{title}</h3>
        <button className="rounded-full border border-[#dfe5dc] px-3 py-2 text-sm font-bold">
          Edit
        </button>
      </div>
      <div className="mt-3 divide-y divide-[#edf1ea]">
        {rows.map(([label, value]) => (
          <div className="flex justify-between gap-4 py-3 text-sm" key={label}>
            <span className="text-[#647067]">{label}</span>
            <span className="max-w-[58%] text-right font-bold">{value}</span>
          </div>
        ))}
      </div>
    </section>
  );
}

function BottomNav({
  activeTab,
  onChange
}: {
  activeTab: Tab;
  onChange: (tab: Tab) => void;
}) {
  return (
    <nav className="absolute bottom-0 left-0 right-0 border-t border-black/5 bg-white/95 px-3 pb-4 pt-2 backdrop-blur">
      <div className="grid grid-cols-4 gap-1">
        {navItems.map((item) => {
          const Icon = item.icon;
          const isActive = activeTab === item.id;
          return (
            <button
              className={`flex min-h-14 flex-col items-center justify-center gap-1 rounded-lg text-xs font-black ${
                isActive ? "bg-[#e8f7d1] text-[#1f7a4d]" : "text-[#647067]"
              }`}
              key={item.id}
              onClick={() => onChange(item.id)}
            >
              <Icon size={20} />
              {item.label}
            </button>
          );
        })}
      </div>
    </nav>
  );
}

function InfoRow({
  icon: Icon,
  label,
  value
}: {
  icon: typeof CalendarDays;
  label: string;
  value: string;
}) {
  return (
    <div className="flex items-start gap-3">
      <span className="mt-0.5 grid h-8 w-8 shrink-0 place-items-center rounded-full bg-[#edf1ea] text-[#1f7a4d]">
        <Icon size={16} />
      </span>
      <span>
        <span className="block text-xs font-bold uppercase tracking-wide text-[#647067]">
          {label}
        </span>
        <span className="font-bold text-[#17201b]">{value}</span>
      </span>
    </div>
  );
}

function MiniStat({ label, value }: { label: string; value: string }) {
  return (
    <div className="rounded-xl border border-[#edf1ee] bg-[#f7faf7] p-2 text-center">
      <p className="text-[10px] font-bold uppercase tracking-[0.12em] text-[#647067]">{label}</p>
      <p className="mt-1 text-base font-black text-[#171d1a]">{value}</p>
    </div>
  );
}

function StatusBadge({ status }: { status: MatchRequest["status"] }) {
  const classes = {
    Accepted: "bg-[#e8f7d1] text-[#1f7a4d]",
    Pending: "bg-[#fff4d6] text-[#8a5c00]",
    "Needs reply": "bg-[#ffe8e4] text-[#b13b2d]"
  };

  return (
    <span className={`shrink-0 rounded-full px-3 py-1 text-xs font-black ${classes[status]}`}>
      {status}
    </span>
  );
}

function IconButton({ label, children }: { label: string; children: React.ReactNode }) {
  return (
    <button
      aria-label={label}
      className="grid h-10 w-10 place-items-center rounded-full border border-[#dfe5dc] bg-white text-[#17201b]"
      title={label}
    >
      {children}
    </button>
  );
}

function EmptyState({ text }: { text: string }) {
  return (
    <div className="rounded-lg border border-dashed border-[#b8c3b9] bg-white p-8 text-center">
      <ChevronLeft className="mx-auto text-[#1f7a4d]" size={30} />
      <p className="mt-3 font-bold text-[#647067]">{text}</p>
    </div>
  );
}
