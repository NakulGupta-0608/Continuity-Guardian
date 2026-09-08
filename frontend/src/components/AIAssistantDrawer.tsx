import React, { useState } from 'react';
import { 
  Bot, 
  X, 
  Send, 
  Sparkles, 
  Wrench, 
  CheckCircle2, 
  ArrowRight,
  ShieldCheck,
  Film
} from 'lucide-react';
import { api } from '../services/api';

interface Message {
  id: string;
  sender: 'user' | 'agent';
  text: string;
  toolCalls?: Array<{ tool: string; arguments?: any }>;
  actionOffer?: {
    action: string;
    title: string;
    payload: any;
  };
  timestamp: string;
}

interface AIAssistantDrawerProps {
  isOpen: boolean;
  onClose: () => void;
  projectId: string;
  onStateModified: () => void;
}

export const AIAssistantDrawer: React.FC<AIAssistantDrawerProps> = ({
  isOpen,
  onClose,
  projectId,
  onStateModified
}) => {
  const [input, setInput] = useState('');
  const [isLoading, setIsLoading] = useState(false);
  const [messages, setMessages] = useState<Message[]>([
    {
      id: 'init_1',
      sender: 'agent',
      text: "👋 Hello Director. I am your **Continuity Guardian Autonomous Agent**. I continuously verify characters, props, locations, timeline chronology, and wardrobe across all shooting scripts.\n\nAsk me about prop locations, character inconsistencies, or request state repairs.",
      timestamp: new Date().toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' })
    }
  ]);

  const presetQuestions = [
    "Where was the red notebook last seen?",
    "Show all continuity errors involving Rahul.",
    "What changed between scenes 10 and 15?",
    "Fix the wardrobe continuity issue.",
    "Why is Scene 11 flagged?"
  ];

  const handleSend = async (userText: string) => {
    if (!userText.trim() || isLoading) return;

    const userMsg: Message = {
      id: `usr_${Date.now()}`,
      sender: 'user',
      text: userText,
      timestamp: new Date().toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' })
    };

    setMessages((prev) => [...prev, userMsg]);
    setInput('');
    setIsLoading(true);

    try {
      const response = await api.chatAgent(projectId, userText);
      const agentMsg: Message = {
        id: `agt_${Date.now()}`,
        sender: 'agent',
        text: response.reply || "State verified.",
        toolCalls: response.tool_calls || [],
        actionOffer: response.action_offer,
        timestamp: new Date().toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' })
      };
      setMessages((prev) => [...prev, agentMsg]);
      
      if (response.resolved_issue_id || response.action_offer) {
        onStateModified();
      }
    } catch (err: any) {
      setMessages((prev) => [
        ...prev,
        {
          id: `err_${Date.now()}`,
          sender: 'agent',
          text: `⚠️ Agent Error: ${err.message || 'Unable to query project state.'}`,
          timestamp: new Date().toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' })
        }
      ]);
    } finally {
      setIsLoading(false);
    }
  };

  const executeActionOffer = async (offer: any) => {
    setIsLoading(true);
    try {
      await handleSend(`Apply recommended fix: ${offer.title}`);
      onStateModified();
    } catch (err) {
      console.error(err);
    } finally {
      setIsLoading(false);
    }
  };

  if (!isOpen) return null;

  return (
    <div className="fixed inset-y-0 right-0 w-full sm:w-[460px] bg-[#0c1017] border-l border-[#20283b] z-50 flex flex-col shadow-2xl">
      
      {/* Drawer Header */}
      <div className="p-4 border-b border-[#1d2535] bg-[#111622] flex items-center justify-between">
        <div className="flex items-center gap-2.5">
          <div className="p-2 rounded-lg bg-amber-500/20 text-amber-400 border border-amber-500/30">
            <Bot className="w-5 h-5" />
          </div>
          <div>
            <h2 className="text-sm font-bold text-white uppercase tracking-wider flex items-center gap-1.5">
              Continuity Agent Copilot
            </h2>
            <p className="text-[10px] text-slate-400">Autonomous production assistant with Gemini tool-calling</p>
          </div>
        </div>

        <button
          onClick={onClose}
          className="p-1.5 rounded-lg text-slate-400 hover:text-white hover:bg-slate-800 transition-colors cursor-pointer"
        >
          <X className="w-5 h-5" />
        </button>
      </div>

      {/* Preset Quick Queries */}
      <div className="p-3 bg-[#0e121a] border-b border-[#1b2230] overflow-x-auto">
        <div className="text-[10px] text-slate-400 uppercase tracking-wider font-bold mb-1.5">
          Quick Director Queries:
        </div>
        <div className="flex gap-1.5 flex-wrap">
          {presetQuestions.map((q, idx) => (
            <button
              key={idx}
              onClick={() => handleSend(q)}
              className="text-[11px] px-2.5 py-1 rounded bg-[#161c2b] text-slate-300 border border-[#252f44] hover:border-amber-400 hover:text-amber-300 transition-colors whitespace-nowrap cursor-pointer"
            >
              {q}
            </button>
          ))}
        </div>
      </div>

      {/* Message Chat Feed */}
      <div className="flex-1 overflow-y-auto p-4 space-y-4">
        {messages.map((m) => {
          const isAgent = m.sender === 'agent';
          return (
            <div
              key={m.id}
              className={`flex flex-col ${isAgent ? 'items-start' : 'items-end'}`}
            >
              <div className="flex items-center gap-1.5 mb-1 px-1">
                <span className="text-[10px] font-bold text-slate-400 uppercase">
                  {isAgent ? '🤖 Continuity Guardian' : '🎬 Director'}
                </span>
                <span className="text-[9px] text-slate-600 font-mono">{m.timestamp}</span>
              </div>

              <div
                className={`max-w-[92%] p-3.5 rounded-xl text-xs leading-relaxed ${
                  isAgent
                    ? 'bg-[#141926] text-slate-200 border border-[#222a3d] shadow-md'
                    : 'bg-amber-500 text-black font-medium shadow-md'
                }`}
              >
                {/* Agent Tool Execution Badges */}
                {m.toolCalls && m.toolCalls.length > 0 && (
                  <div className="mb-3 space-y-1">
                    {m.toolCalls.map((tc, tidx) => (
                      <div
                        key={tidx}
                        className="flex items-center gap-1.5 text-[10px] font-mono bg-black/40 text-amber-300 px-2 py-0.8 rounded border border-amber-500/20"
                      >
                        <Wrench className="w-3 h-3" />
                        <span>tool: <b>{tc.tool}()</b></span>
                      </div>
                    ))}
                  </div>
                )}

                {/* Body Text */}
                <div className="whitespace-pre-wrap">{m.text}</div>

                {/* Action Offer Button */}
                {m.actionOffer && (
                  <div className="mt-3 pt-3 border-t border-slate-700/60">
                    <button
                      onClick={() => executeActionOffer(m.actionOffer)}
                      className="w-full py-1.5 px-3 bg-amber-500 hover:bg-amber-400 text-black text-[11px] font-bold rounded flex items-center justify-center gap-1.5 shadow-md transition-all cursor-pointer"
                    >
                      <CheckCircle2 className="w-3.5 h-3.5" />
                      <span>{m.actionOffer.title}</span>
                    </button>
                  </div>
                )}
              </div>
            </div>
          );
        })}

        {isLoading && (
          <div className="flex items-center gap-2 text-xs text-amber-400 p-2 font-mono">
            <Bot className="w-4 h-4 animate-bounce" />
            <span>Agent querying movie state & running continuity tools...</span>
          </div>
        )}
      </div>

      {/* Message Input Box */}
      <div className="p-3 border-t border-[#1d2535] bg-[#10141f]">
        <form
          onSubmit={(e) => {
            e.preventDefault();
            handleSend(input);
          }}
          className="flex items-center gap-2"
        >
          <input
            type="text"
            placeholder="Ask agent about props, wardrobe, scenes..."
            value={input}
            onChange={(e) => setInput(e.target.value)}
            className="flex-1 bg-[#0a0d14] text-xs text-white placeholder-slate-500 rounded-lg px-3 py-2 border border-[#232b3d] focus:outline-none focus:border-amber-400"
          />
          <button
            type="submit"
            disabled={!input.trim() || isLoading}
            className="p-2 bg-amber-500 hover:bg-amber-400 disabled:opacity-40 text-black rounded-lg transition-colors cursor-pointer"
          >
            <Send className="w-4 h-4" />
          </button>
        </form>
      </div>

    </div>
  );
};
