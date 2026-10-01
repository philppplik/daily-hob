/* Daily Hob consent. No optional services are currently configured.
 * Before adding one: declare its purpose/provider below, update VERSION and
 * privacy information, then register start/stop handlers via HobConsent.register.
 * Never include an optional script, iframe, pixel or preconnect outside the gate.
 */
(() => {
  'use strict';
  const VERSION = '2026-10-01.1';
  const KEY = 'daily-hob:consent';
  const TTL = 180 * 24 * 60 * 60 * 1000;
  const SERVICES = []; // {id, category: 'analytics'|'media', label, description}
  const categories = {analytics: 'Statistik', media: 'Externe Medien'};
  const handlers = new Map();
  let state = null, previousFocus;
  const script = document.currentScript;
  const privacy = new URL('datenschutz', script.src).href;
  const valid = s => s && s.version === VERSION && Number.isFinite(s.savedAt) &&
    s.savedAt <= Date.now() && s.expiresAt === s.savedAt + TTL && s.expiresAt > Date.now() &&
    s.choices && Object.keys(categories).every(k => typeof s.choices[k] === 'boolean');
  const read = () => { try {const s = JSON.parse(localStorage.getItem(KEY)); return valid(s) ? s : null;} catch (_) {return null;} };
  const allowed = category => valid(state) && state.choices[category] === true && SERVICES.some(s => s.category === category);
  const sync = () => {
    handlers.forEach((h, id) => {
      const service = SERVICES.find(s => s.id === id);
      const on = service && allowed(service.category);
      if (on && !h.running) {h.running = true; try {h.start();} catch (e) {h.running = false; console.error('Consent service failed', id);}}
      if (!on && h.running) {h.running = false; h.stop();}
    });
    window.dispatchEvent(new CustomEvent('hob:consentchange', {detail: {analytics: !!allowed('analytics'), media: !!allowed('media')}}));
  };
  window.HobConsent = Object.freeze({
    allowed: category => !!allowed(category),
    register(id, start, stop) {
      if (!SERVICES.some(s => s.id === id) || handlers.has(id) || typeof start !== 'function' || typeof stop !== 'function') throw new Error('Declare a service and supply start/stop handlers first');
      handlers.set(id, {start, stop, running: false}); sync();
    },
    open: () => open(true)
  });
  const dialog = document.createElement('dialog');
  dialog.className = 'consent';
  dialog.setAttribute('aria-labelledby', 'consent-title');
  dialog.setAttribute('aria-describedby', 'consent-copy');
  dialog.innerHTML = `<button type="button" class="consent-close" aria-label="Ohne Auswahl schließen">×</button><p class="consent-kicker">DEINE DATEN. DEINE WAHL.</p><h2 id="consent-title">Wenig Cookies.<br>Viel Klarheit.</h2><p id="consent-copy">Daily Hob nutzt aktuell keine Tracking-Cookies und keine optionalen Dienste. Nur deine Datenschutz-Auswahl speichern wir lokal in deinem Browser, für 180 Tage. Kein Konto. Kein Tracking.</p><details class="consent-details"><summary>Einstellungen ansehen</summary><div class="consent-category"><div><strong>Notwendig</strong><p>Speichert deine Auswahl nur in diesem Browser. Immer aktiv.</p></div><span class="consent-status">Immer aktiv</span></div><div id="consent-categories"></div><p class="consent-note">Neue Dienste erhalten keine Zustimmung im Voraus. Wenn welche hinzukommen, fragen wir dich erneut.</p></details><p class="consent-privacy"><a href="${privacy}">Datenschutzerklärung</a> · Jederzeit im Footer ändern.</p><p class="consent-feedback" role="status" hidden></p><div class="consent-actions"><button type="button" data-consent="reject">Alles ablehnen</button><button type="button" data-consent="accept">Alles annehmen</button><button type="button" data-consent="save" hidden>Auswahl speichern</button></div>`;
  Object.entries(categories).forEach(([key, label]) => {
    const services = SERVICES.filter(s => s.category === key);
    const row = document.createElement('label'); row.className = 'consent-category';
    const text = document.createElement('div'), strong = document.createElement('strong'), p = document.createElement('p');
    strong.textContent = label;
    p.textContent = services.length ? services.map(s => `${s.label}: ${s.description}`).join(' ') : 'Aktuell nicht verwendet. Es wird nichts geladen.';
    text.append(strong, p);
    const input = document.createElement('input'); input.type = 'checkbox'; input.name = key; input.disabled = !services.length; input.setAttribute('aria-label', label);
    row.append(text, input); dialog.querySelector('#consent-categories').append(row);
  });
  document.body.append(dialog);
  const details = dialog.querySelector('details');
  details.addEventListener('toggle', () => {dialog.querySelector('[data-consent="save"]').hidden = !details.open;});
  function open(settings = false) {
    previousFocus = document.activeElement;
    Object.keys(categories).forEach(k => {dialog.querySelector(`[name="${k}"]`).checked = !!allowed(k);});
    details.open = settings;
    if (!dialog.open) dialog.showModal();
    dialog.querySelector('.consent-close').focus();
  }
  dialog.addEventListener('close', () => {if (previousFocus && previousFocus.isConnected) previousFocus.focus();});
  dialog.querySelector('.consent-close').addEventListener('click', () => dialog.close());
  function save(action) {
    const now = Date.now(); const choices = {};
    Object.keys(categories).forEach(k => {choices[k] = SERVICES.some(s => s.category === k) && (action === 'accept' || (action === 'save' && dialog.querySelector(`[name="${k}"]`).checked));});
    const revoked = Object.keys(categories).some(k => allowed(k) && !choices[k]);
    state = {version: VERSION, savedAt: now, expiresAt: now + TTL, choices};
    let persisted = true;
    try {localStorage.setItem(KEY, JSON.stringify(state));} catch (_) {persisted = false;}
    sync();
    if (persisted) dialog.close();
    else {const status = dialog.querySelector('.consent-feedback'); status.hidden = false; status.textContent = 'Deine Auswahl gilt für diese Seite. Dein Browser verhindert das Speichern; beim nächsten Besuch fragen wir erneut.';}
    // A fresh document also stops third-party timers and in-flight integrations.
    if (revoked) location.reload();
  }
  dialog.querySelectorAll('[data-consent]').forEach(b => b.addEventListener('click', () => save(b.dataset.consent)));
  document.querySelectorAll('[data-consent-open]').forEach(b => {b.hidden = false; b.addEventListener('click', () => open(true));});
  state = read(); sync();
  if (!state) open();
  window.addEventListener('storage', e => {if (e.key === KEY || e.key === null) {state = read(); sync(); if (!state) open();}});
  const checkExpiry = () => {if (state && !valid(state)) {state = null; sync(); open();}};
  document.addEventListener('visibilitychange', checkExpiry);
  setInterval(checkExpiry, 60 * 1000);
})();
(function(){
var API='https://daily-hob-newsletter.vercel.app/api/subscribe';
var q=new URLSearchParams(location.search).get('status');
var T=document.getElementById('nl-status-title'),X=document.getElementById('nl-status-text');
if(T&&X&&q){var m={bestaetigt:['Du bist dabei.','Danke, deine Anmeldung ist bestätigt. Das nächste Hob Friday Signal oder der nächste Hob Monday Rewind landet in deinem Postfach.'],ungueltig:['Link abgelaufen.','Dieser Bestätigungslink ist ungültig oder älter als 48 Stunden. Trag dich unten einfach noch einmal ein.'],fehler:['Das hat nicht geklappt.','Beim Bestätigen ist etwas schiefgelaufen. Versuch es bitte später noch einmal.']}[q];if(m){T.textContent=m[0];X.textContent=m[1]}}
document.querySelectorAll('.nl-form').forEach(function(f){
f.addEventListener('submit',function(e){e.preventDefault();
var msg=f.querySelector('.nl-msg'),btn=f.querySelector('.nl-btn'),em=f.elements.email,c=f.elements.consent;
msg.className='nl-msg';
if(!em.value||!/^[^\s@]+@[^\s@]+\.[^\s@]{2,}$/.test(em.value.trim())){msg.textContent='Bitte gib eine gültige E-Mail-Adresse ein.';msg.classList.add('err');em.focus();return}
if(!c.checked){msg.textContent='Bitte bestätige zuerst die Einwilligung.';msg.classList.add('err');return}
btn.disabled=true;msg.textContent='Einen Moment …';
fetch(API,{method:'POST',headers:{'Content-Type':'application/json'},body:JSON.stringify({email:em.value.trim(),consent:true,website:f.elements.website.value})})
.then(function(r){return r.json().then(function(j){return{r:r,j:j}})})
.then(function(o){if(o.r.ok&&o.j.ok){f.reset();msg.textContent='Fast geschafft: Wir haben dir eine Bestätigungsmail geschickt. Klick auf den Link darin, dann bist du dabei. Schau ggf. auch im Spam-Ordner nach.';msg.classList.add('ok')}else if(o.r.status===429){msg.textContent='Zu viele Versuche. Bitte probier es später noch einmal.';msg.classList.add('err')}else{msg.textContent='Das hat leider nicht geklappt. Bitte prüf die Adresse und versuch es noch einmal.';msg.classList.add('err')}})
.catch(function(){msg.textContent='Keine Verbindung. Bitte versuch es später noch einmal.';msg.classList.add('err')})
.then(function(){btn.disabled=false})})})})();
