import {
  AbsoluteFill,
  Audio,
  Img,
  Sequence,
  staticFile,
  interpolate,
  useCurrentFrame,
  useVideoConfig,
} from "remotion";

export type ImageClip = {
  src: string;
  startInFrames: number;
  durationInFrames: number;
};

export type Caption = {
  text: string;
  startMs: number;
  endMs: number;
};

export type Bgm = {
  src: string;
  volume: number;
  fadeInFrames: number;
  fadeOutFrames: number;
};

export type TemplateProps = {
  audioSrc: string;
  images: ImageClip[];
  captions: Caption[];
  title?: string;
  bgm?: Bgm;
  // banner 템플릿 전용(다른 템플릿은 무시).
  headlineMain?: string;
  headlineAccent?: string;
  channelName?: string;
  footerMain?: string;
  footerAccent?: string;
  accentColor?: string;
};

// 배경음악: 음성 대비 낮은 볼륨 + fade in/out. loop로 영상 길이에 맞춰 자동 반복/트림.
// 음원이 없으면(props.bgm 없음) 아무것도 렌더하지 않음(안전 fallback).
export const BgmTrack = ({ bgm }: { bgm?: Bgm }) => {
  const { durationInFrames } = useVideoConfig();
  if (!bgm) return null;
  const { src, volume, fadeInFrames, fadeOutFrames } = bgm;
  const volumeAt = (f: number) => {
    const fadeIn =
      fadeInFrames > 0
        ? interpolate(f, [0, fadeInFrames], [0, 1], { extrapolateLeft: "clamp", extrapolateRight: "clamp" })
        : 1;
    const fadeOut =
      fadeOutFrames > 0
        ? interpolate(f, [durationInFrames - fadeOutFrames, durationInFrames], [1, 0], {
            extrapolateLeft: "clamp",
            extrapolateRight: "clamp",
          })
        : 1;
    return volume * Math.min(fadeIn, fadeOut);
  };
  return <Audio src={staticFile(src)} loop volume={volumeAt} />;
};

// 한 이미지의 Ken Burns 줌(시퀀스 내부 프레임 기준).
export const KenBurnsImage = ({
  src,
  durationInFrames,
  to = 1.12,
}: {
  src: string;
  durationInFrames: number;
  to?: number;
}) => {
  const frame = useCurrentFrame();
  const scale = interpolate(frame, [0, durationInFrames], [1, to], {
    extrapolateRight: "clamp",
  });
  return (
    <AbsoluteFill style={{ overflow: "hidden" }}>
      <Img
        src={staticFile(src)}
        style={{
          width: "100%",
          height: "100%",
          objectFit: "cover",
          transform: `scale(${scale})`,
        }}
      />
    </AbsoluteFill>
  );
};

// 배경 이미지들을 순서대로(각자 Ken Burns) 깔아줌.
export const BackgroundImages = ({
  images,
  to = 1.12,
}: {
  images: ImageClip[];
  to?: number;
}) => (
  <>
    {images.map((img, i) => (
      <Sequence key={i} from={img.startInFrames} durationInFrames={img.durationInFrames}>
        <KenBurnsImage src={img.src} durationInFrames={img.durationInFrames} to={to} />
      </Sequence>
    ))}
  </>
);

// 현재 프레임 시각에 해당하는 자막 텍스트(없으면 null).
export const useCurrentCaption = (captions: Caption[]): string | null => {
  const frame = useCurrentFrame();
  const { fps } = useVideoConfig();
  const ms = (frame / fps) * 1000;
  const c = captions.find((x) => ms >= x.startMs && ms < x.endMs);
  return c ? c.text : null;
};
