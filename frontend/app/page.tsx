"use client";

import { CalendarDays, Check, CirclePlus, Compass, LogOut, Users, X } from "lucide-react";
import { FormEvent, useEffect, useMemo, useState } from "react";
import DiscoverView, { type DiscoverCard } from "./discover-view";

const API = process.env.NEXT_PUBLIC_API_BASE_URL ?? "http://127.0.0.1:8010/api/v1";
type Tab = "clubs" | "games" | "discover" | "requests" | "profile";
type Skill = "beginner" | "casual" | "intermediate" | "advanced";

type User = { id: string; phone_number: string; display_name: string; city: string; is_captain: boolean };
type Club = { id: string; owner_id: string; name: string; city: string; area: string; home_turf: string; description: string; skill_level: Skill; availability: string; play_style: string; rating: number; player_count: number };
type Member = { id: string; club_id: string; user_id: string; display_name: string; phone_number: string; role: "owner" | "player"; status: "pending" | "active" | "removed"; position?: string; skill_level?: Skill };
type Game = { id: string; club_id: string; club_name: string; venue: string; venue_area: string; scheduled_at: string; cost_per_person: string; skill_level: Skill; format: string; host_player_target: number; host_open_slots: number; accepted_players: number; pending_players: number; status: string; opponent_club_id?: string; opponent_club_name?: string };
type Challenge = { id: string; game_id: string; host_club_id: string; host_club_name: string; challenger_club_id: string; challenger_club_name: string; status: string; confirmed_at?: string };

async function api<T>(path: string, token?: string | null, options?: RequestInit): Promise<T> {
  const response = await fetch(`${API}${path}`, {
    ...options,
    headers: {
      "Content-Type": "application/json",
      ...(token ? { Authorization: `Bearer ${token}` } : {}),
      ...(options?.headers ?? {})
    }
  });
  const body = await response.json().catch(() => null);
  if (!response.ok) throw new Error(body?.detail ?? "Something went wrong. Please try again.");
  return body as T;
}

const fieldClass = "mt-1 w-full rounded-md border border-slate-300 bg-white px-3 py-2 text-sm outline-none focus:border-emerald-600";
const buttonClass = "inline-flex items-center justify-center gap-2 rounded-md bg-emerald-700 px-3 py-2 text-sm font-semibold text-white hover:bg-emerald-800 disabled:cursor-not-allowed disabled:opacity-50";

export default function HomePage() {
  const [token, setToken] = useState<string | null>(null);
  const [user, setUser] = useState<User | null>(null);
  const [tab, setTab] = useState<Tab>("clubs");
  const [clubs, setClubs] = useState<Club[]>([]);
  const [games, setGames] = useState<Game[]>([]);
  const [clubGames, setClubGames] = useState<Game[]>([]);
  const [fixtures, setFixtures] = useState<Challenge[]>([]);
  const [selectedClubId, setSelectedClubId] = useState<string>("");
  const [members, setMembers] = useState<Member[]>([]);
  const [joinRequests, setJoinRequests] = useState<Member[]>([]);
  const [cards, setCards] = useState<DiscoverCard[]>([]);
  const [challenges, setChallenges] = useState<Challenge[]>([]);
  const [outgoingChallenges, setOutgoingChallenges] = useState<Challenge[]>([]);
  const [notice, setNotice] = useState<string>("");
  const [error, setError] = useState<string>("");

  const ownedClubs = useMemo(() => clubs.filter((club) => club.owner_id === user?.id), [clubs, user]);
  const selectedClub = ownedClubs.find((club) => club.id === selectedClubId) ?? ownedClubs[0];

  useEffect(() => {
    const savedToken = window.localStorage.getItem("turfmatch-token");
    if (savedToken) setToken(savedToken);
  }, []);

  useEffect(() => {
    if (token) void loadApp();
  }, [token]);

  useEffect(() => {
    if (token && selectedClub) void loadClubWorkspace(selectedClub.id);
  }, [token, selectedClubId, clubs.length]);

  async function loadApp() {
    if (!token) return;
    try {
      const [me, clubList, upcoming, fixtureList] = await Promise.all([
        api<User>("/users/me", token),
        api<Club[]>("/clubs"),
        api<Game[]>("/users/me/games/upcoming", token),
        api<Challenge[]>("/fixtures", token)
      ]);
      setUser(me);
      setClubs(clubList);
      setGames(upcoming);
      setFixtures(fixtureList);
      const firstOwned = clubList.find((club) => club.owner_id === me.id);
      if (firstOwned && !selectedClubId) setSelectedClubId(firstOwned.id);
    } catch (loadError) {
      setError(loadError instanceof Error ? loadError.message : "Unable to load TurfMatch.");
    }
  }

  async function loadClubWorkspace(clubId: string) {
    if (!token) return;
    try {
      const [memberList, challengeList, cardList, gameList, pendingMembers, outgoing] = await Promise.all([
        api<Member[]>(`/clubs/${clubId}/members`, token),
        api<Challenge[]>(`/clubs/${clubId}/challenges/incoming`, token),
        api<DiscoverCard[]>(`/match-cards/feed?club_id=${clubId}`, token),
        api<Game[]>(`/clubs/${clubId}/games`),
        api<Member[]>(`/clubs/${clubId}/join-requests`, token),
        api<Challenge[]>(`/clubs/${clubId}/challenges/outgoing`, token)
      ]);
      setMembers(memberList);
      setChallenges(challengeList);
      setCards(cardList);
      setOutgoingChallenges(outgoing);
      setClubGames(gameList);
      setJoinRequests(pendingMembers);
    } catch (loadError) {
      setError(loadError instanceof Error ? loadError.message : "Unable to load club workspace.");
    }
  }

  function onAuthenticated(auth: { access_token: string; user: User }) {
    window.localStorage.setItem("turfmatch-token", auth.access_token);
    setUser(auth.user);
    setToken(auth.access_token);
    setNotice("Welcome to TurfMatch.");
  }

  function logout() {
    window.localStorage.removeItem("turfmatch-token");
    setToken(null);
    setUser(null);
    setClubs([]);
    setGames([]);
    setClubGames([]);
    setCards([]);
    setChallenges([]);
    setOutgoingChallenges([]);
    setJoinRequests([]);
  }

  async function joinClub(clubId: string) {
    try {
      await api(`/clubs/${clubId}/join-requests`, token, { method: "POST" });
      setNotice("Join request sent to the club owner.");
    } catch (requestError) {
      setError(requestError instanceof Error ? requestError.message : "Unable to send request.");
    }
  }

  async function decideChallenge(id: string, approve: boolean) {
    try {
      await api(`/challenges/${id}/decision`, token, { method: "POST", body: JSON.stringify({ approve }) });
      setNotice(approve ? "Fixture confirmed." : "Challenge declined.");
      await loadApp();
      if (selectedClub) await loadClubWorkspace(selectedClub.id);
    } catch (requestError) {
      setError(requestError instanceof Error ? requestError.message : "Unable to decide challenge.");
    }
  }

  async function decideMembership(id: string, approve: boolean) {
    try {
      await api(`/club-members/${id}/decision`, token, { method: "POST", body: JSON.stringify({ approve }) });
      setNotice(approve ? "Player added to the club." : "Join request declined.");
      await loadApp();
      if (selectedClub) await loadClubWorkspace(selectedClub.id);
    } catch (requestError) {
      setError(requestError instanceof Error ? requestError.message : "Unable to decide join request.");
    }
  }

  async function swipe(card: DiscoverCard, direction: "like" | "pass"): Promise<boolean> {
    if (!selectedClub) return false;
    try {
      await api(`/match-cards/${card.id}/swipe`, token, { method: "POST", body: JSON.stringify({ club_id: selectedClub.id, direction }) });
      setNotice(direction === "like" ? "Game request sent. The host captain will review it." : "Card passed.");
      await loadClubWorkspace(selectedClub.id);
      return true;
    } catch (requestError) {
      setError(requestError instanceof Error ? requestError.message : "Unable to act on card.");
      return false;
    }
  }

  if (!token || !user) return <AuthScreen onAuthenticated={onAuthenticated} />;

  return (
    <main className="phone-shell flex min-h-screen flex-col bg-slate-50">
      <header className="border-b border-slate-200 bg-white px-4 py-3">
        <p className="text-xs font-semibold uppercase tracking-[0.16em] text-emerald-700">TurfMatch</p>
        <div className="mt-1 flex items-center justify-between gap-3">
          <div><h1 className="text-xl font-bold text-slate-950">Bengaluru football</h1><p className="text-sm text-slate-500">8v8 club fixtures</p></div>
          <span className="rounded-full bg-emerald-50 px-2 py-1 text-xs font-semibold text-emerald-800">{user.display_name}</span>
        </div>
      </header>

      <section className="flex-1 px-4 py-4 pb-24">
        {(notice || error) && <div className={`mb-4 flex items-start justify-between gap-2 rounded-md border px-3 py-2 text-sm ${error ? "border-red-200 bg-red-50 text-red-800" : "border-emerald-200 bg-emerald-50 text-emerald-800"}`}><span>{error || notice}</span><button aria-label="Dismiss" onClick={() => { setNotice(""); setError(""); }}><X size={16} /></button></div>}
        {tab === "clubs" && <ClubsView clubs={clubs} ownedClubs={ownedClubs} onJoin={joinClub} onCreated={async () => { await loadApp(); setTab("profile"); }} token={token} onError={setError} onNotice={setNotice} />}
        {tab === "games" && <GamesView token={token} games={games} clubGames={clubGames} ownedClubs={ownedClubs} selectedClub={selectedClub} members={members} onRefresh={async () => { await loadApp(); if (selectedClub) await loadClubWorkspace(selectedClub.id); }} onNotice={setNotice} onError={setError} />}
        {tab === "discover" && <DiscoverView cards={cards} clubName={selectedClub?.name} onSwipe={swipe} />}
        {tab === "requests" && <RequestsView joinRequests={joinRequests} challenges={challenges} outgoingChallenges={outgoingChallenges} fixtures={fixtures} onMembershipDecision={decideMembership} onDecision={decideChallenge} />}
        {tab === "profile" && <ProfileView user={user} ownedClubs={ownedClubs} selectedClubId={selectedClub?.id ?? ""} onClubChange={setSelectedClubId} onLogout={logout} />}
      </section>

      <nav className="fixed bottom-0 left-1/2 flex w-full max-w-[480px] -translate-x-1/2 border-t border-slate-200 bg-white">
        {[
          ["clubs", "Clubs", Users], ["games", "Games", CalendarDays], ["discover", "Discover", Compass], ["requests", "Requests", Check], ["profile", "Profile", LogOut]
        ].map(([id, label, Icon]) => <button key={id as string} onClick={() => setTab(id as Tab)} className={`flex min-h-16 flex-1 flex-col items-center justify-center gap-1 text-[11px] font-medium ${tab === id ? "text-emerald-700" : "text-slate-500"}`}><Icon size={18} /><span>{label as string}</span></button>)}
      </nav>
    </main>
  );
}

function AuthScreen({ onAuthenticated }: { onAuthenticated: (auth: { access_token: string; user: User }) => void }) {
  const [mode, setMode] = useState<"login" | "signup">("login");
  const [error, setError] = useState("");
  async function submit(event: FormEvent<HTMLFormElement>) {
    event.preventDefault();
    const data = new FormData(event.currentTarget);
    try {
      const body = mode === "login"
        ? { phone_number: data.get("phone"), password: data.get("password") }
        : { phone_number: data.get("phone"), password: data.get("password"), display_name: data.get("name"), skill_level: data.get("skill"), position: data.get("position") };
      const auth = await api<{ access_token: string; user: User }>(`/auth/${mode}`, undefined, { method: "POST", body: JSON.stringify(body) });
      onAuthenticated(auth);
    } catch (submitError) { setError(submitError instanceof Error ? submitError.message : "Unable to continue."); }
  }
  return <main className="phone-shell min-h-screen bg-slate-50 px-5 py-12"><div className="mx-auto max-w-sm"><p className="text-sm font-semibold uppercase tracking-[0.16em] text-emerald-700">TurfMatch</p><h1 className="mt-3 text-3xl font-bold text-slate-950">Bengaluru 8v8 football.</h1><p className="mt-2 text-sm leading-6 text-slate-600">Create a club, fill your roster, and find a confirmed opponent.</p><form onSubmit={submit} className="mt-8 space-y-4 rounded-lg border border-slate-200 bg-white p-4 shadow-sm">{mode === "signup" && <><label className="block text-sm font-medium">Name<input required name="name" className={fieldClass} /></label><label className="block text-sm font-medium">Position<select name="position" className={fieldClass}><option>Flexible</option><option>Goalkeeper</option><option>Defender</option><option>Midfielder</option><option>Winger</option><option>Striker</option></select></label><label className="block text-sm font-medium">Skill<select name="skill" className={fieldClass}><option value="casual">Casual</option><option value="beginner">Beginner</option><option value="intermediate">Intermediate</option><option value="advanced">Advanced</option></select></label></>}<label className="block text-sm font-medium">Phone number<input required name="phone" placeholder="+919000000001" className={fieldClass} /></label><label className="block text-sm font-medium">Password<input required name="password" type="password" minLength={8} className={fieldClass} /></label>{error && <p className="text-sm text-red-700">{error}</p>}<button className={`${buttonClass} w-full`} type="submit">{mode === "login" ? "Log in" : "Create account"}</button></form><button className="mt-4 text-sm font-semibold text-emerald-700" onClick={() => { setMode(mode === "login" ? "signup" : "login"); setError(""); }}>{mode === "login" ? "Need an account? Sign up" : "Already have an account? Log in"}</button><p className="mt-8 rounded-md bg-slate-200 px-3 py-2 text-xs text-slate-600">Demo owner: <strong>+919000000001</strong><br />Password: <strong>turfmatch123</strong></p></div></main>;
}

function ClubsView({ clubs, ownedClubs, onJoin, onCreated, token, onError, onNotice }: { clubs: Club[]; ownedClubs: Club[]; onJoin: (id: string) => void; onCreated: () => Promise<void>; token: string; onError: (value: string) => void; onNotice: (value: string) => void }) {
  const [creating, setCreating] = useState(false);
  async function create(event: FormEvent<HTMLFormElement>) { event.preventDefault(); const data = new FormData(event.currentTarget); try { await api("/clubs", token, { method: "POST", body: JSON.stringify({ name: data.get("name"), area: data.get("area"), home_turf: data.get("turf"), description: data.get("description"), skill_level: data.get("skill"), availability: data.get("availability"), play_style: data.get("style") }) }); setCreating(false); onNotice("Club created. You are its owner."); await onCreated(); } catch (e) { onError(e instanceof Error ? e.message : "Unable to create club."); } }
  return <div className="space-y-4"><div className="flex items-center justify-between"><div><h2 className="text-xl font-bold">Clubs</h2><p className="text-sm text-slate-500">Find a Bengaluru football community.</p></div><button className={buttonClass} onClick={() => setCreating(!creating)}><CirclePlus size={16} /> Create</button></div>{creating && <form onSubmit={create} className="space-y-3 rounded-lg border border-slate-200 bg-white p-4"><input required name="name" placeholder="Club name" className={fieldClass} /><input required name="area" placeholder="Area, e.g. Indiranagar" className={fieldClass} /><input required name="turf" placeholder="Home turf" className={fieldClass} /><textarea required name="description" placeholder="Short club description" className={fieldClass} /><select name="skill" className={fieldClass}><option value="casual">Casual</option><option value="intermediate">Intermediate</option><option value="advanced">Advanced</option></select><input required name="availability" placeholder="Availability, e.g. Friday after 8 PM" className={fieldClass} /><input required name="style" placeholder="Play style" className={fieldClass} /><button className={buttonClass}>Save club</button></form>}<div className="space-y-3">{clubs.map((club) => <article key={club.id} className="rounded-lg border border-slate-200 bg-white p-4"><div className="flex items-start justify-between gap-3"><div><h3 className="font-bold text-slate-950">{club.name}</h3><p className="mt-1 text-sm text-slate-500">{club.area} · {club.skill_level} · {club.player_count} members</p></div><span className="text-sm font-semibold text-amber-600">{club.rating.toFixed(1)}</span></div><p className="mt-3 text-sm text-slate-600">{club.description}</p><p className="mt-2 text-xs text-slate-500">{club.home_turf} · {club.availability}</p>{!ownedClubs.some((own) => own.id === club.id) && <button className={`${buttonClass} mt-3`} onClick={() => onJoin(club.id)}>Request to join</button>}</article>)}</div></div>;
}

function GamesView({ token, games, clubGames, ownedClubs, selectedClub, members, onRefresh, onNotice, onError }: { token: string; games: Game[]; clubGames: Game[]; ownedClubs: Club[]; selectedClub?: Club; members: Member[]; onRefresh: () => Promise<void>; onNotice: (value: string) => void; onError: (value: string) => void }) {
  const [creating, setCreating] = useState(false); const [activeGame, setActiveGame] = useState<Game | null>(null); const [selectedPlayers, setSelectedPlayers] = useState<string[]>([]);
  async function create(event: FormEvent<HTMLFormElement>) { event.preventDefault(); if (!selectedClub) return; const data = new FormData(event.currentTarget); try { await api(`/clubs/${selectedClub.id}/games`, token, { method: "POST", body: JSON.stringify({ venue: data.get("venue"), venue_area: data.get("area"), scheduled_at: new Date(String(data.get("time"))).toISOString(), cost_per_person: Number(data.get("cost")), skill_level: data.get("skill") }) }); setCreating(false); onNotice("Draft game created. Invite eight members next."); await onRefresh(); } catch (e) { onError(e instanceof Error ? e.message : "Unable to create game."); } }
  async function invite() { if (!activeGame || selectedPlayers.length === 0) return; try { await api(`/games/${activeGame.id}/invitations`, token, { method: "POST", body: JSON.stringify({ player_ids: selectedPlayers }) }); onNotice("Invitations sent."); setActiveGame(null); setSelectedPlayers([]); await onRefresh(); } catch (e) { onError(e instanceof Error ? e.message : "Unable to invite players."); } }
  async function respond(game: Game, value: "accepted" | "rejected") { try { await api(`/games/${game.id}/respond`, token, { method: "POST", body: JSON.stringify({ status: value }) }); onNotice(`Game ${value}.`); await onRefresh(); } catch (e) { onError(e instanceof Error ? e.message : "Unable to respond."); } }
  async function publish(game: Game) { try { await api(`/games/${game.id}/publish`, token, { method: "POST" }); onNotice("Game published for an opponent club."); await onRefresh(); } catch (e) { onError(e instanceof Error ? e.message : "Unable to publish game."); } }
  const activeMembers = members.filter((member) => member.status === "active");
  const displayGames = [...clubGames, ...games.filter((game) => !clubGames.some((clubGame) => clubGame.id === game.id))];
  return <div className="space-y-4"><div className="flex items-center justify-between"><div><h2 className="text-xl font-bold">Games</h2><p className="text-sm text-slate-500">Fill eight players before publishing.</p></div>{selectedClub && <button className={buttonClass} onClick={() => setCreating(!creating)}><CirclePlus size={16} /> New game</button>}</div>{ownedClubs.length === 0 && <p className="rounded-md bg-slate-100 p-3 text-sm text-slate-600">Create a club first to schedule a game.</p>}{creating && <form onSubmit={create} className="space-y-3 rounded-lg border border-slate-200 bg-white p-4"><input required name="venue" placeholder="Turf name" className={fieldClass} /><input required name="area" placeholder="Turf area" className={fieldClass} /><input required name="time" type="datetime-local" className={fieldClass} /><input required name="cost" type="number" min="0" placeholder="Cost per player" className={fieldClass} /><select name="skill" className={fieldClass}><option value="casual">Casual</option><option value="intermediate">Intermediate</option><option value="advanced">Advanced</option></select><button className={buttonClass}>Create draft</button></form>}{activeGame && <section className="rounded-lg border border-emerald-200 bg-emerald-50 p-4"><h3 className="font-bold">Invite club members</h3><p className="mt-1 text-sm text-slate-600">Select up to eight players for this game.</p><div className="mt-3 space-y-2">{activeMembers.map((member) => <label key={member.id} className="flex items-center gap-2 text-sm"><input type="checkbox" checked={selectedPlayers.includes(member.user_id)} disabled={!selectedPlayers.includes(member.user_id) && selectedPlayers.length >= 8} onChange={() => setSelectedPlayers((values) => values.includes(member.user_id) ? values.filter((id) => id !== member.user_id) : [...values, member.user_id])} />{member.display_name} <span className="text-slate-500">{member.position}</span></label>)}</div><div className="mt-3 flex gap-2"><button className={buttonClass} onClick={invite}>Send invitations ({selectedPlayers.length})</button><button className="rounded-md border border-slate-300 px-3 py-2 text-sm" onClick={() => setActiveGame(null)}>Cancel</button></div></section>}<div className="space-y-3">{displayGames.map((game) => <article key={game.id} className="rounded-lg border border-slate-200 bg-white p-4"><div className="flex justify-between gap-2"><div><h3 className="font-bold">{game.club_name} · {game.format}</h3><p className="mt-1 text-sm text-slate-600">{new Date(game.scheduled_at).toLocaleString()} · {game.venue}</p></div><span className="rounded bg-slate-100 px-2 py-1 text-xs font-semibold">{game.status.replaceAll("_", " ")}</span></div><p className="mt-3 text-sm">Host roster: <strong>{game.accepted_players}/8 accepted</strong> · {game.host_open_slots} open</p>{game.opponent_club_name && <p className="mt-1 text-sm text-emerald-700">Opponent: {game.opponent_club_name}</p>}<div className="mt-3 flex flex-wrap gap-2">{selectedClub?.id === game.club_id && ["draft", "broadcasting"].includes(game.status) && <button className={buttonClass} onClick={() => setActiveGame(game)}>Invite players</button>}{selectedClub?.id === game.club_id && game.status === "roster_filled" && <button className={buttonClass} onClick={() => publish(game)}>Publish for opponent</button>}{selectedClub?.id !== game.club_id && ["broadcasting", "roster_filled"].includes(game.status) && <><button className={buttonClass} onClick={() => respond(game, "accepted")}>Accept</button><button className="rounded-md border border-slate-300 px-3 py-2 text-sm" onClick={() => respond(game, "rejected")}>Decline</button></>}</div></article>)}{displayGames.length === 0 && <p className="rounded-md bg-slate-100 p-3 text-sm text-slate-600">No games yet.</p>}</div></div>;
}


function RequestsView({
  joinRequests,
  challenges,
  outgoingChallenges,
  fixtures,
  onMembershipDecision,
  onDecision
}: {
  joinRequests: Member[];
  challenges: Challenge[];
  outgoingChallenges: Challenge[];
  fixtures: Challenge[];
  onMembershipDecision: (id: string, approve: boolean) => void;
  onDecision: (id: string, approve: boolean) => void;
}) {
  const pendingIncoming = challenges.filter((item) => item.status === "pending");

  return (
    <div className="space-y-5">
      <div>
        <h2 className="text-xl font-bold">Requests</h2>
        <p className="mt-1 text-sm text-slate-500">Player joins and club game requests.</p>
      </div>

      <section>
        <h3 className="text-sm font-bold uppercase text-slate-500">Sent game requests</h3>
        <div className="mt-2 space-y-2">
          {outgoingChallenges.map((item) => (
            <article key={item.id} className="rounded-md border border-slate-200 bg-white p-4">
              <p className="font-semibold">{item.host_club_name}</p>
              <p className="mt-1 text-sm text-slate-600">Playing as {item.challenger_club_name}</p>
              <p className="mt-2 text-xs font-semibold capitalize text-emerald-700">{item.status}</p>
            </article>
          ))}
          {outgoingChallenges.length === 0 && <p className="rounded-md bg-slate-100 p-3 text-sm text-slate-600">No requests sent yet.</p>}
        </div>
      </section>

      <section>
        <h3 className="text-sm font-bold uppercase text-slate-500">Incoming challenges</h3>
        <div className="mt-2 space-y-2">
          {pendingIncoming.map((item) => (
            <article key={item.id} className="rounded-md border border-slate-200 bg-white p-4">
              <p className="font-semibold">{item.challenger_club_name}</p>
              <p className="mt-1 text-sm text-slate-600">Wants to play {item.host_club_name}</p>
              <div className="mt-3 flex gap-2">
                <button className={buttonClass} onClick={() => onDecision(item.id, true)}>Confirm fixture</button>
                <button className="rounded-md border border-slate-300 px-3 py-2 text-sm" onClick={() => onDecision(item.id, false)}>Decline</button>
              </div>
            </article>
          ))}
          {pendingIncoming.length === 0 && <p className="rounded-md bg-slate-100 p-3 text-sm text-slate-600">No incoming challenges.</p>}
        </div>
      </section>

      <section>
        <h3 className="text-sm font-bold uppercase text-slate-500">Player join requests</h3>
        <div className="mt-2 space-y-2">
          {joinRequests.map((item) => (
            <article key={item.id} className="rounded-md border border-slate-200 bg-white p-4">
              <p className="font-semibold">{item.display_name}</p>
              <p className="mt-1 text-sm text-slate-600">{item.position ?? "Flexible"} · {item.skill_level ?? "casual"}</p>
              <div className="mt-3 flex gap-2">
                <button className={buttonClass} onClick={() => onMembershipDecision(item.id, true)}>Approve</button>
                <button className="rounded-md border border-slate-300 px-3 py-2 text-sm" onClick={() => onMembershipDecision(item.id, false)}>Decline</button>
              </div>
            </article>
          ))}
          {joinRequests.length === 0 && <p className="rounded-md bg-slate-100 p-3 text-sm text-slate-600">No pending player requests.</p>}
        </div>
      </section>

      <section>
        <h3 className="text-sm font-bold uppercase text-slate-500">Confirmed fixtures</h3>
        <div className="mt-2 space-y-2">
          {fixtures.map((item) => (
            <article key={item.id} className="rounded-md border border-emerald-200 bg-emerald-50 p-4">
              <p className="font-semibold">{item.host_club_name} vs {item.challenger_club_name}</p>
              <p className="mt-1 text-sm text-emerald-800">Confirmed 8v8 fixture</p>
            </article>
          ))}
          {fixtures.length === 0 && <p className="rounded-md bg-slate-100 p-3 text-sm text-slate-600">No confirmed fixtures yet.</p>}
        </div>
      </section>
    </div>
  );
}

function ProfileView({ user, ownedClubs, selectedClubId, onClubChange, onLogout }: { user: User; ownedClubs: Club[]; selectedClubId: string; onClubChange: (value: string) => void; onLogout: () => void }) { return <div className="space-y-4"><div><h2 className="text-xl font-bold">Profile</h2><p className="mt-1 text-sm text-slate-500">{user.phone_number} · {user.city}</p></div>{ownedClubs.length > 0 && <label className="block rounded-lg border border-slate-200 bg-white p-4 text-sm font-medium">Active owner club<select value={selectedClubId} onChange={(event) => onClubChange(event.target.value)} className={fieldClass}>{ownedClubs.map((club) => <option key={club.id} value={club.id}>{club.name}</option>)}</select></label>}<button className="inline-flex items-center gap-2 rounded-md border border-slate-300 px-3 py-2 text-sm font-semibold" onClick={onLogout}><LogOut size={16} /> Log out</button></div>; }
