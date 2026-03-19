# ChartSpeak

ChartSpeak is an accessibility-focused prototype that helps blind and low-vision users explore bar charts through sound.

Instead of only offering a short text summary, ChartSpeak lets users detect charts on screen, hear spoken context, and listen to the data as tones. In the current version, the app supports **bar charts only**.

## What It Does

ChartSpeak is designed for moments when a chart appears in a class slide, article, dashboard, report, or presentation and a screen reader alone is not enough.

The app works like this:

- it captures the current screen
- detects visible bar charts
- extracts chart values
- converts the bars into sound
- lets the user move through detected charts with keyboard shortcuts

Higher bars play as higher pitches, which helps the user hear comparisons, patterns, and differences between categories.

## Why It Matters

Charts are everywhere, but they are still largely inaccessible. A sighted user can quickly inspect trends, compare categories, and notice outliers. A blind user often gets only a vague description or no useful information at all.

ChartSpeak is meant to preserve that sense of independent exploration by turning chart data into an interactive audio experience.

## Current Scope

This repository is an early-stage prototype. Right now, ChartSpeak focuses only on **bar chart sonification**.

The broader vision includes support for other chart types, but that functionality is not implemented yet.

## Running The App

Start the app with:

```bash
python main.py
```

ChartSpeak runs in the macOS menu bar and listens for global keyboard shortcuts.

## Setup

Install dependencies with:

```bash
pip install -r requirements.txt
```

The app is currently built for **macOS** and may require:

- Accessibility permission for global hotkeys
- Screen Recording permission for screen capture

## Keyboard Shortcuts

- `Command + Control + Option + C`: detect bar charts on the current screen
- `Command + Control + Option + R`: start reading the detected charts
- `Command + Control + Option + N`: go to the next chart
- `Command + Control + Option + P`: go to the previous chart
- `Command + Control + Option + A`: replay the current chart
- `Command + Control + Option + Q`: exit the app

You can also adjust the pitch range while listening:

- `Control + Option + Shift + Up Arrow`: raise the low note
- `Control + Option + Shift + Down Arrow`: lower the low note
- `Control + Option + Up Arrow`: raise the high note
- `Control + Option + Down Arrow`: lower the high note

## Recommended Workflow

1. Open the page, slide, or document that contains a bar chart.
2. Make sure the chart is visible on screen.
3. Press `Command + Control + Option + C` to detect charts.
4. Press `Command + Control + Option + R` to begin playback.
5. Use the navigation shortcuts to move between charts or replay the current one.

The app uses spoken feedback and audio playback, so it pairs well with screen readers such as VoiceOver.

## Notes

- The current version is best understood as a prototype.
- Only bar charts are supported right now.
- Depending on the current app mode, chart extraction may use either dummy data or Gemini-based extraction.
- The project’s main goal is to make visual data more independently explorable through sound.
