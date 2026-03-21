/**
 * Integration tests for MiniMax TypeScript SDK -- Music module (lyrics only).
 *
 * Only tests generateLyrics() to avoid consuming audio generation credits.
 *
 * Run with: cd typescript && npx vitest run tests/integration/music.test.ts
 */

import { describe, it, expect } from "vitest";
import MiniMax from "../../src/index.js";

const client = new MiniMax();

describe("Music generateLyrics()", () => {
  it("generates full song lyrics", async () => {
    const result = await client.music.generateLyrics("write_full_song", {
      prompt: "A cheerful summer love song",
    });

    console.log(`\n  title=${result.song_title}`);
    console.log(`  style=${result.style_tags}`);
    console.log(`  lyrics=${result.lyrics.slice(0, 100)}...`);

    expect(result.song_title).toBeTruthy();
    expect(result.style_tags).toBeTruthy();
    expect(result.lyrics.length).toBeGreaterThan(0);
    expect(result.lyrics).toContain("[");
  });

  it("edits existing lyrics", async () => {
    const original = await client.music.generateLyrics("write_full_song", {
      prompt: "A sad ballad about rain",
    });

    const edited = await client.music.generateLyrics("edit", {
      lyrics: original.lyrics,
      prompt: "Make it more upbeat",
    });

    console.log(`\n  original title=${original.song_title}`);
    console.log(`  edited title=${edited.song_title}`);

    expect(edited.lyrics.length).toBeGreaterThan(0);
  });
});
