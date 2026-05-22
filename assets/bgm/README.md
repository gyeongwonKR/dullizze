# BGM 음원

템플릿별 기본 배경음악을 여기에 둔다. 파일이 없으면 BGM 없이 정상 렌더된다(안전 fallback).

| 파일명 | 사용 템플릿 |
|---|---|
| `documentary.mp3` | documentary |
| `pop.mp3` | pop |

- **반드시 로열티프리/라이선스 확보된 음원만** 사용(PRD §16 저작권).
- 볼륨/페이드는 코드에서 처리하므로 원본 그대로 두면 된다. 조절은 `.env`:
  - `BGM_VOLUME_DB` (기본 -22, 음성 우선)
  - `BGM_FADE_MS` (기본 800)
  - `BGM_ENABLED=0`이면 전체 비활성화.
- 길이는 영상에 맞춰 자동 loop/trim(Remotion `<Audio loop>`).
