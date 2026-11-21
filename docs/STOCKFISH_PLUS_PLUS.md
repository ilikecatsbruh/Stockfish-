# Stockfish++ development plan

This fork keeps Stockfish's proven search and position infrastructure as the baseline.

## Reusable move cache

Stockfish already implements the reusable move cache as part of its transposition table (TT). Each entry is indexed by the Zobrist position key and stores a best move, searched value, static evaluation, depth, bound, and generation. Search probes the TT before move ordering and can reuse the stored move as its TT move.

Important behavior:
- TT entries survive ordinary successive `go` searches, so positions reached again later in a game can reuse prior work.
- `Hash` controls the table size in MiB.
- `Clear Hash` explicitly clears it.
- A new root search advances the generation rather than clearing the table.
- The table is shared by search threads and uses Stockfish's existing collision/aging policy.

Do not add a second independent move cache: it would duplicate TT storage, add synchronization and invalidation risks, and compete for memory. Any future cache work should improve TT replacement, observability, or measured hit rate and must be tested for Elo.

## Transformer integration boundary

The repository currently uses Stockfish NNUE in `src/evaluate.cpp`. The 1B transformer is not wired into this source tree yet. A safe integration needs its exact model contract:
- input encoding and tensor shape/dtype;
- inference runtime and model file format;
- output semantics (centipawn score, WDL logits/probabilities, or another target);
- score perspective (side-to-move or White).

Once those are known, add it behind a selectable UCI evaluation option while retaining NNUE as the default/fallback. Do not invoke a 1B model at every leaf until latency is measured. Benchmark selective inference, batching, and position-keyed result caching before enabling it in the main search.

## Validation

The GitHub Actions workflow builds the engine, checks the start-position perft(5) count (4,865,609), and runs Stockfish's built-in benchmark. These are correctness and performance-regression checks, not proof of Elo gain. Playing-strength changes still require paired self-play testing with enough games and a fixed hardware/time-control setup.
