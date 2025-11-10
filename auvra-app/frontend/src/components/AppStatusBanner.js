import React, { useEffect, useState } from 'react';
import { View, Text, StyleSheet, TouchableOpacity } from 'react-native';
import { API_BASE_URL } from '../services/api';
import { checkBackendHealth } from '../utils/health';

// Lightweight global status banner to show backend connectivity & latency.
export default function AppStatusBanner() {
  const [status, setStatus] = useState({ ok: true, latencyMs: null, checking: true });
  const [expanded, setExpanded] = useState(false);

  async function runCheck() {
    setStatus(s => ({ ...s, checking: true }));
    const result = await checkBackendHealth(API_BASE_URL);
    setStatus({ ...result, checking: false });
  }

  useEffect(() => {
    runCheck();
    const id = setInterval(runCheck, 30000); // refresh every 30s
    return () => clearInterval(id);
  }, []);

  const color = status.checking ? '#F0AD4E' : status.ok ? '#3BB273' : '#D9534F';
  const label = status.checking ? 'Checking…' : status.ok ? 'Online' : 'Offline';

  return (
    <TouchableOpacity activeOpacity={0.9} onPress={() => setExpanded(e => !e)} style={styles.touchWrap}>
      <View style={[styles.banner, { borderColor: color, shadowColor: color }]}> 
        <View style={[styles.dot, { backgroundColor: color }]} />
        <Text style={styles.text}>{label}</Text>
        {status.latencyMs != null && !status.checking && (
          <Text style={styles.latency}>{status.latencyMs} ms</Text>
        )}
        <Text style={styles.hint}>tap</Text>
      </View>
      {expanded && (
        <View style={styles.panel}>
          <Text style={styles.panelLine}>API: {API_BASE_URL}</Text>
          {status.error && <Text style={styles.panelError}>Error: {status.error}</Text>}
          <TouchableOpacity style={styles.refreshBtn} onPress={runCheck}>
            <Text style={styles.refreshText}>Re-check now</Text>
          </TouchableOpacity>
        </View>
      )}
    </TouchableOpacity>
  );
}

const styles = StyleSheet.create({
  touchWrap: { position: 'absolute', top: 6, left: 10, right: 10, zIndex: 9999 },
  banner: {
    flexDirection: 'row',
    alignItems: 'center',
    backgroundColor: '#FFFFFFEE',
    borderRadius: 14,
    paddingHorizontal: 12,
    paddingVertical: 6,
    borderWidth: 2,
    shadowOpacity: 0.15,
    shadowRadius: 4,
    shadowOffset: { width: 0, height: 2 },
  },
  dot: {
    width: 10,
    height: 10,
    borderRadius: 5,
    marginRight: 8,
  },
  text: { fontWeight: '600', color: '#333' },
  latency: { marginLeft: 8, fontSize: 12, color: '#555' },
  hint: { marginLeft: 'auto', fontSize: 11, color: '#888' },
  panel: { marginTop: 6, backgroundColor: '#FFF', borderRadius: 12, padding: 12, borderWidth: 1, borderColor: '#E5D4F1' },
  panelLine: { fontSize: 12, color: '#444', marginBottom: 4 },
  panelError: { fontSize: 12, color: '#D9534F', marginBottom: 6 },
  refreshBtn: { alignSelf: 'flex-start', backgroundColor: '#B565A7', paddingHorizontal: 10, paddingVertical: 6, borderRadius: 8 },
  refreshText: { color: '#FFF', fontSize: 12, fontWeight: '600' },
});
