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

export type MainProps = {
  fps: number;
  width: number;
  height: number;
  durationInFrames: number;
  audioSrc: string;
  images: ImageClip[];
  captions: Caption[];
};

const KenBurns = ({ src, durationInFrames }: { src: string; durationInFrames: number }) => {
  const frame = useCurrentFrame();
  const scale = interpolate(frame, [0, durationInFrames], [1, 1.12], {
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

const CaptionView = ({ text }: { text: string }) => (
  <AbsoluteFill
    style={{
      justifyContent: "flex-end",
      alignItems: "center",
      padding: "0 60px 340px",
    }}
  >
    <div
      style={{
        fontFamily: "'NanumGothic', sans-serif",
        fontSize: 88,
        fontWeight: 800,
        color: "white",
        textAlign: "center",
        lineHeight: 1.25,
        WebkitTextStroke: "10px black",
        paintOrder: "stroke fill",
      }}
    >
      {text}
    </div>
  </AbsoluteFill>
);

export const Main = ({ audioSrc, images, captions }: MainProps) => {
  const frame = useCurrentFrame();
  const { fps } = useVideoConfig();
  const ms = (frame / fps) * 1000;
  const current = captions.find((c) => ms >= c.startMs && ms < c.endMs);

  return (
    <AbsoluteFill style={{ backgroundColor: "black" }}>
      <Audio src={staticFile(audioSrc)} />
      {images.map((img, i) => (
        <Sequence
          key={i}
          from={img.startInFrames}
          durationInFrames={img.durationInFrames}
        >
          <KenBurns src={img.src} durationInFrames={img.durationInFrames} />
        </Sequence>
      ))}
      {current ? <CaptionView text={current.text} /> : null}
    </AbsoluteFill>
  );
};
